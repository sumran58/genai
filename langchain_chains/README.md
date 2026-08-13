# LangChain — Chains

Composing prompts, models and parsers into pipelines with LCEL. Four topologies: simple, sequential, parallel, and conditional.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white)

---

## Contents

- [The idea](#the-idea)
- [Setup](#setup)
- [The four topologies](#the-four-topologies)
- [Runnable primitives](#runnable-primitives)
- [What chains actually give you](#what-chains-actually-give-you)
- [Known issues](#known-issues)

---

## The idea

Prompts, models and parsers all implement the same `Runnable` interface, so they compose with `|`:

```python
chain = prompt | model | parser
```

Each step's output becomes the next step's input. Once components share an interface, wiring them together stops requiring glue code — and the resulting object gets `.batch()`, `.stream()`, async, and tracing for free.

These four scripts walk through the shapes that composition can take: one step after another, several at once, and branching on a condition.

Every script ends with:

```python
chain.get_graph().print_ascii()
```

which draws the chain's structure in the terminal. Run it — seeing the graph for the parallel and conditional versions is more instructive than reading the code.

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

## The four topologies

### 1. Simple — `simple_chain.py`

```python
chain = prompt | model | parser
result = chain.invoke({'topic': 'cricket'})
```

The baseline. Three components, one line, one model call.

```
{'topic': 'cricket'} → PromptTemplate → PromptValue → ChatGroq → AIMessage → StrOutputParser → str
```

`StrOutputParser` unwraps `.content` from the `AIMessage`. Small job, but it's what lets a chain end in a plain string instead of an object you have to unpack.

### 2. Sequential — `sequential_chain.py`

```python
chain = prompt1 | model | parser | prompt2 | model | parser
```

Generate a detailed report, then summarise it. **Two model calls**, output of the first feeding the second.

There's a subtlety worth knowing here. A `PromptTemplate` normally expects a dict, but `prompt2` receives a bare string from the parser. It works because `prompt2` has exactly **one** input variable — LangChain lets a single bare value through and assigns it to that variable. With two variables the same chain raises:

```
TypeError: Expected mapping type as input to PromptTemplate.
```

So this pattern is convenient but conditional. Multi-variable steps need a `RunnableParallel` or `RunnableLambda` to build the dict, which is exactly what the next script does.

### 3. Parallel — `parallel_chain.py`

```python
parallel_chain = RunnableParallel({
    'notes': prompt1 | model | parser,
    'quiz':  prompt2 | model | parser
})
merge_chain = prompt3 | model | parser
chain = parallel_chain | merge_chain
```

From one text, produce notes and a quiz **at the same time**, then merge them.

`RunnableParallel` takes a dict of branches, runs them concurrently against the same input, and returns a dict with the same keys. That output dict — `{'notes': ..., 'quiz': ...}` — maps directly onto `prompt3`'s two input variables, which is why the merge step works without any manual assembly.

The concurrency is real: two independent API calls go out together, so the wall-clock cost is roughly one call rather than two. That's the whole reason to reach for this shape — any time steps don't depend on each other, running them in sequence wastes time.

### 4. Conditional — `conditional_chain.py`

```python
classifier_chain = prompt1 | model | parser2      # → Feedback(sentiment=...)

branch_chain = RunnableBranch(
    (lambda x: x.sentiment == 'Positive', prompt3 | model | parser),
    (lambda x: x.sentiment == 'Negative', prompt2 | model | parser),
    RunnableLambda(lambda x: "could not find the sentiment")
)
chain = classifier_chain | branch_chain
```

Classify feedback, then route to a different response chain depending on the result.

`RunnableBranch` takes `(condition, runnable)` pairs plus a mandatory final default. It evaluates conditions top to bottom and runs the first match.

The default has to be a `Runnable`, which a bare string isn't — hence `RunnableLambda`, which wraps any Python function into the interface. That's the general escape hatch: whenever you need arbitrary logic inside a chain, `RunnableLambda` is how it gets in.

Using `PydanticOutputParser` for the classifier is what makes the branch conditions safe. `Literal['Positive', 'Negative']` guarantees the value is one of exactly two strings, so `x.sentiment == 'Positive'` can't be defeated by the model replying `"positive"` or `"POSITIVE"`.

**This script has a real bug** — the routed prompts never see the original feedback text. See [Known issues](#known-issues) item 1.

---

## Runnable primitives

| Primitive | Purpose |
|---|---|
| `\|` | Sequence — output of one becomes input of the next |
| `RunnableParallel` | Run branches concurrently, return a dict |
| `RunnableBranch` | Route to one of several chains based on a condition |
| `RunnableLambda` | Wrap any Python function as a chain step |
| `RunnablePassthrough` | Forward input unchanged — used to carry a value past a step |

`RunnablePassthrough` isn't in these scripts, but it's the missing piece for the conditional bug below: it's how you keep the original input available to later steps instead of losing it.

---

## What chains actually give you

Beyond tidier code, every composed chain gets:

- **`.batch([...])`** — process many inputs, parallelised
- **`.stream(...)`** — token-by-token output
- **`.ainvoke(...)`** — async, same shape
- **`.get_graph().print_ascii()`** — visualise the structure
- **LangSmith tracing** — every step's input and output, if enabled

None of that is implemented by the prompt or the model individually. It comes from the shared `Runnable` interface, which is the actual argument for composing this way rather than calling `.invoke()` by hand.

---

## Known issues

Verified against `langchain-core` 1.5.3.

**1. `conditional_chain.py` loses the feedback text before the response is written.**

`classifier_chain` returns a `Feedback` object. `RunnableBranch` passes that object to `prompt2` / `prompt3`, which have a single `{feedback}` variable — so the single-variable shortcut applies and the *whole Feedback object* gets stringified into the slot. Reproduced:

```
"Write an appropriate response to this negative feedback \n sentiment='Negative'"
```

The model is asked to respond to the literal text `sentiment='Negative'`. It never sees `"it was a terrible experience"`. You still get a plausible-looking reply — a generic apology for an unspecified problem — which is what makes this easy to miss.

The fix is to carry the original text alongside the sentiment:

```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

classifier_chain = RunnableParallel({
    'sentiment': prompt1 | model | parser2 | RunnableLambda(lambda f: f.sentiment),
    'feedback':  RunnableLambda(lambda x: x['feedback']),
})

branch_chain = RunnableBranch(
    (lambda x: x['sentiment'] == 'Positive', prompt3 | model | parser),
    (lambda x: x['sentiment'] == 'Negative', prompt2 | model | parser),
    RunnableLambda(lambda x: "could not find the sentiment")
)
```

Note the conditions change from `x.sentiment` to `x['sentiment']` — the branch now receives a dict, not a `Feedback` object. Verified output after the fix:

```
'Respond to this negative feedback \n it was a terrible experience'
```

This is worth sitting with, because it's the general hazard of sequential chains: **each step only sees the previous step's output.** Anything from earlier in the pipeline that a later step needs has to be explicitly threaded through. `RunnableParallel` and `RunnablePassthrough` are the two tools for that.

**2. `requirements.txt` doesn't list `pydantic`.** `conditional_chain.py` imports `BaseModel` and `Field` directly. It works today because langchain pulls pydantic in transitively, but a direct import belongs in the file:

```
langchain
langchain-core
langchain-groq
pydantic
python-dotenv
```

**3. The sentiment classifier has no neutral option.** `Literal['Positive', 'Negative']` forces every input into one of two buckets, including genuinely neutral feedback like *"the package arrived on Tuesday"*. The `RunnableBranch` default is therefore unreachable — nothing the parser can return will fall through to it. If you want that default to mean something, add a third value:

```python
sentiment: Literal['Positive', 'Negative', 'Neutral']
```

**4. Unused imports in `conditional_chain.py`.** `RunnableParallel` is imported but never used. Harmless, but it becomes useful once you apply the fix in item 1.

**5. Typo in the prompt text.** `prompt2` and `prompt3` both say `reponse` instead of `response`. The model will cope, but the typo is going into the prompt.
