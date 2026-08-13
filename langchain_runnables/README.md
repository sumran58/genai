# LangChain — Runnables

The five primitives that LCEL is built from, each in its own script. Sequence, parallel, passthrough, lambda, branch — declared explicitly rather than hidden behind the `|` operator.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white)

---

## Contents

- [The idea](#the-idea)
- [Setup](#setup)
- [The five primitives](#the-five-primitives)
- [Reference table](#reference-table)
- [The input-shape rule](#the-input-shape-rule)
- [Known issues](#known-issues)

---

## The idea

`prompt | model | parser` is syntax sugar. Underneath, `|` constructs a `RunnableSequence`. These scripts write the classes out by hand so the machinery is visible:

```python
chain = RunnableSequence(prompt, model, parser)   # identical to prompt | model | parser
```

Nobody writes production code this way — the operator is shorter and reads better. But building each primitive explicitly makes clear that a "chain" isn't a special LangChain concept. It's a small set of composable objects that all implement one interface, and once you know the five, you can build any topology.

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

`.env` in the project root:

```env
GROQ_API_KEY=your_groq_key
```

> Check `.env` is in `.gitignore` before the first commit.

Free key at [console.groq.com](https://console.groq.com).

---

## The five primitives

### 1. `RunnableSequence` — `runnable_sequence.py`

```python
chain = RunnableSequence(prompt, model, parser)
print(chain.invoke({'topic': 'cricket'}))
```

Runs steps in order, feeding each output into the next.

```
{'topic': 'cricket'} → PromptValue → AIMessage → str
```

This is exactly what `prompt | model | parser` produces. Verify it yourself with `type(prompt | model | parser)`.

### 2. `RunnableParallel` — `runnable_parallel.py`

```python
chain = RunnableParallel({
    'tweet':    RunnableSequence(prompt1, model, parser),
    'linkedin': RunnableSequence(prompt2, model, parser)
})
```

Takes a dict of branches, gives **all of them the same input**, runs them concurrently, and returns a dict with the same keys.

Both branches receive `{'topic': 'cricket'}`. Output:

```python
{'tweet': '...', 'linkedin': '...'}
```

The concurrency is real — two API calls go out together, so the wall-clock cost is roughly one call, not two. That's the reason to use this any time steps don't depend on each other.

The dict keys are also how you shape data for a later step: if a downstream prompt has variables `{tweet}` and `{linkedin}`, this output plugs straight in.

### 3. `RunnablePassthrough` — `runnable_passthrough.py`

```python
parallel_chain = RunnableParallel({
    'joke': RunnablePassthrough(),
    'explanation': RunnableSequence(prompt2, model, parser)
})
chain = RunnableSequence(gen_chain, parallel_chain)
```

`RunnablePassthrough` returns its input unchanged. On its own that sounds pointless — its purpose is **keeping a value alive** through a step that would otherwise consume it.

In a plain sequence, each step only sees the previous step's output. The original text is gone. Inside a `RunnableParallel`, one key can be a passthrough while another key transforms, so you end up with both:

```python
{'joke': '<the generated text>', 'explanation': '<the model output>'}
```

This is the standard fix for "the later step needs something from earlier in the chain" — the single most common structural problem in LCEL.

The key names in this script are copy-paste leftovers; see [Known issues](#known-issues) item 2.

### 4. `RunnableLambda` — `runnable_lambda.py`

```python
parallel_chain = RunnableParallel({
    'joke': RunnablePassthrough(),
    'word_count': RunnableLambda(lambda x: len(x.split()))
})
```

Wraps any Python function into the `Runnable` interface, so plain logic — counting, cleaning, reformatting, calling an API — can live inside a chain.

The commented-out block at the top of the file shows it standalone:

```python
def word_counter(text):
    return len(text.split())
runnable_word_counter = RunnableLambda(word_counter)
runnable_word_counter.invoke('hi my name is simran')   # → 5
```

Worth uncommenting once. Seeing a bare function gain `.invoke()` is what makes the "everything is a Runnable" idea concrete.

This is the general escape hatch. Anything LangChain doesn't provide a primitive for, you write as a function and wrap.

### 5. `RunnableBranch` — `runnable_branch.py`

```python
branch_chain = RunnableBranch(
    (condition, runnable),
    RunnablePassthrough()     # mandatory default
)
```

Conditional routing. Takes `(condition, runnable)` pairs plus a required final default, evaluates conditions top to bottom, and runs the first match.

The intent in this script is: generate a report, and summarise it **only if it's long**. Short reports pass through untouched.

The condition as written doesn't do that — see [Known issues](#known-issues) item 1.

Note that the default must be a `Runnable`. A bare value won't work; wrap it in `RunnableLambda` if you need one.

---

## Reference table

| Primitive | Input → Output | Use when |
|---|---|---|
| `RunnableSequence` | chained | Steps depend on each other |
| `RunnableParallel` | one input → dict | Steps are independent; run them concurrently |
| `RunnablePassthrough` | `x` → `x` | A later step needs an earlier value |
| `RunnableLambda` | `x` → `f(x)` | Arbitrary Python inside a chain |
| `RunnableBranch` | `x` → matched branch | Routing on a condition |

---

## The input-shape rule

Most chain bugs come from a step receiving a shape it didn't expect. Two rules cover nearly all of them:

**A `PromptTemplate` normally needs a dict.** The exception is when it has exactly **one** input variable — then a bare value is accepted and assigned to it. That's why `RunnableSequence(gen_chain, prompt2, model, parser)` works when `prompt2` has a single `{topic}`. Give it two variables and the same chain raises:

```
TypeError: Expected mapping type as input to PromptTemplate.
```

**Each step sees only the previous step's output.** Anything from earlier in the pipeline has to be threaded through deliberately — via `RunnableParallel` with a `RunnablePassthrough` key, which is exactly what primitive 3 exists for.

---

## Known issues

Verified against `langchain-core` 1.5.3.

**1. The branch condition in `runnable_branch.py` returns a number, not a boolean.**

```python
(lambda x: len(x.split()), RunnableSequence(prompt2, model, parser))
```

`len(...)` is an `int`, and every non-zero int is truthy — so the branch matches for any non-empty input. The report is **always** summarised, and `RunnablePassthrough()` is unreachable unless the model returns an empty string. Reproduced:

```
'one two three' -> 'SUMMARIZED::one two three'
'aaaaa'         -> 'SUMMARIZED::aaaaa'
''              -> ''
```

The intended behaviour needs a comparison:

```python
branch_chain = RunnableBranch(
    (lambda x: len(x.split()) > 300, RunnableSequence(prompt2, model, parser)),
    RunnablePassthrough()
)
```

Now short reports pass through and only long ones get summarised — which is what makes the passthrough default meaningful.

This is worth noticing generally: a `RunnableBranch` condition is evaluated for truthiness, not checked for being a bool. Returning a length, a list, or a dict by accident silently produces a branch that always fires.

**2. Key and variable names in `runnable_passthrough.py` are copy-paste leftovers.** The chain generates a *summary*, but the variable is `joke_gen_chain` and the output key is `'joke'`:

```python
{'joke': '<a summary about cricket>', 'explanation': '...'}
```

Nothing breaks, but the output is mislabelled. Rename to `summary_gen_chain` and `'summary'`.

Related: `prompt2` reads `'generate a linkedin post about {topic}'`, and what it actually receives is the full summary text via the single-variable shortcut. Confirmed:

```
'explanation': "PROMPT2 GOT: 'SUMMARY TEXT ABOUT CRICKET'"
```

So the model is asked to write a LinkedIn post *about the summary text*, which works but isn't what the variable name `{topic}` suggests. Renaming it to `{text}` would make the intent readable.

**3. `requirements.txt` uses an underscore.** `langchain_groq` should be `langchain-groq` — the PyPI package name uses a hyphen. pip normalises this, so it installs either way, but the hyphenated form is correct and matches your other repos.

**4. Duplicate import.** Every script imports `PromptTemplate` twice. Harmless, worth cleaning.

**5. Unused imports.** `runnable_parallel.py` and others import primitives they don't use (`RunnablePassthrough`, `RunnableBranch`). Since each script is meant to demonstrate one primitive, trimming to just what's used would make each file read more clearly.
