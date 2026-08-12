# LangChain — Output Parsers

Turning raw model output into usable Python, and chaining steps together with LCEL. Four parsers, from "just give me the string" to "validate it against a Pydantic model".

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?logo=huggingface&logoColor=black)

---

## Contents

- [The problem](#the-problem)
- [Setup](#setup)
- [Scripts](#scripts)
- [Which parser to use](#which-parser-to-use)
- [Parsers vs `with_structured_output`](#parsers-vs-with_structured_output)
- [How the chain operator works](#how-the-chain-operator-works)
- [Known issues](#known-issues)

---

## The problem

A model returns an `AIMessage`. To get the text you write `result.content`, and to get structured data out of that text you write parsing code by hand.

Output parsers handle both, and — more importantly — they're **chainable**. Because a parser implements the same `Runnable` interface as prompts and models, the whole pipeline composes with `|`:

```python
chain = template1 | model | parser | template2 | model | parser
result = chain.invoke({'topic': 'black hole'})
```

Two model calls, two prompts, all the glue removed. That composition is what these scripts build toward.

The other half of the job is the **format instruction**. Parsers generate text explaining the required output format, which gets injected into the prompt via `partial_variables`. The parser tells the model what to produce and then parses what comes back — both sides from one object.

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
HUGGINGFACEHUB_ACCESS_TOKEN=your_hf_token
```

Every script reads this explicitly with `os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")` and passes it to `HuggingFaceEndpoint`. Note this is a custom name — LangChain's own default is `HUGGINGFACEHUB_API_TOKEN`, which it would pick up automatically. Both work; just keep the `.env` key matching what the code asks for.

> Check `.env` is in `.gitignore` before the first commit.

Token from [huggingface.co](https://huggingface.co) → Settings → Access Tokens. Read scope is enough.

---

## Scripts

### `stroutputparser.py` — the problem, written out longhand

Two prompts and two model calls, wired manually:

```python
prompt1 = template1.invoke({'topic': 'black hole'})
result = model.invoke(prompt1)

prompt2 = template2.invoke({'text': result.content})
result1 = model.invoke(prompt2)
print(result1.content)
```

Write a report, then summarise the report. It works, and it shows exactly what's happening — but every step is manual: unwrap `.content`, build the next input dict, invoke again. Four lines of plumbing for two useful operations.

`StrOutputParser` is imported here but never used. That's deliberate as a before/after pair with the next file.

### `stroutputparser1.py` — the same thing as a chain

```python
parser = StrOutputParser()
chain = template1 | model | parser | template2 | model | parser
result = chain.invoke({'topic': 'black hole'})
```

Identical behaviour, one line.

`StrOutputParser` does one thing: takes an `AIMessage` and returns `.content` as a plain string. Trivial on its own — but it's what makes the chain flow, because `template2` needs text, not a message object.

Worth understanding *why* the string from the first parser slots into `template2` without a dict. A `PromptTemplate` normally expects a mapping. When it has exactly **one** input variable, LangChain lets a bare value through and assigns it to that variable. Confirmed by running it — and confirmed that with two variables it fails:

```
TypeError: Expected mapping type as input to PromptTemplate.
```

So this chain works because `template2` happens to have a single `{text}` variable. Add a second and the chain breaks, and you'd need a `RunnableLambda` or `RunnablePassthrough` to build the dict. Convenient, but not a general rule.

### `structuredoutputparser.py` — named fields

```python
response_schemas = [
    ResponseSchema(name="summary", description="A short summary of the topic"),
    ResponseSchema(name="facts",   description="Important facts about the topic"),
    ResponseSchema(name="analogy", description="A simple analogy to explain the topic"),
]
parser = StructuredOutputParser.from_response_schemas(response_schemas)
```

`get_format_instructions()` turns those schemas into text telling the model to return a markdown-fenced JSON object with exactly those keys. Injected through `partial_variables`, it becomes part of the prompt.

`partial_variables` is the right mechanism here: the format instruction is fixed, so it's filled at construction time, leaving `topic` as the only thing `.invoke()` has to supply.

Returns a `dict`. The keys are guaranteed to be the three you named — but nothing checks the *values*. Every field is implicitly a string, and there's no way to say "facts should be a list" or "age must be at least 18".

### `jsonoutputparser.py` — free-form JSON

```python
parser = JsonOutputParser()
template1 = PromptTemplate(
    template="give me the name, age and the city of the fictional person.\n {format_instruction}",
    partial_variables={'format_instruction': parser.get_format_instructions()}
)
```

`JsonOutputParser` asks for valid JSON and parses it — but imposes **no schema**. You describe the fields in prose and hope the model uses the key names you expect. `name`/`age`/`city` or `full_name`/`years`/`location` are both valid JSON, and the parser accepts either.

Useful when the shape genuinely varies. A liability when downstream code expects specific keys.

Note this script uses `.format()` rather than `.invoke()`. `format()` returns a plain string, `invoke()` returns a `PromptValue`. Both work with a chat model; `invoke()` is the one that composes into chains.

### `pydantic_outputpasers.py` — schema plus validation

```python
class Person(BaseModel):
    name: str = Field(description='name of the person')
    age: int = Field(ge=18, description="Age of the person")
    city: str = Field(...)

parser = PydanticOutputParser(pydantic_object=Person)
```

The strongest option. `get_format_instructions()` emits the model's full JSON Schema — field names, types, and descriptions — so the model gets a precise specification rather than prose.

More importantly, parsing **validates**. If the model returns `age: 15`, the `ge=18` constraint raises rather than letting bad data through. `StructuredOutputParser` and `JsonOutputParser` would both accept it.

Returns a real `Person` object: `result.name`, autocomplete in the editor, type checking.

The `city` field in this file has a bug — see [Known issues](#known-issues) item 1.

---

## Which parser to use

| | StrOutputParser | JsonOutputParser | StructuredOutputParser | PydanticOutputParser |
|---|---|---|---|---|
| Returns | `str` | `dict` | `dict` | **object** |
| Enforces key names | — | No | **Yes** | **Yes** |
| Enforces types | — | No | No | **Yes** |
| Value constraints (`ge`, regex) | — | No | No | **Yes** |
| Nested structures | — | Yes | Awkward | **Yes** |
| Extra dependency | No | No | No | pydantic |

**`StrOutputParser`** whenever the output is prose, and as the connector between chain steps.

**`PydanticOutputParser`** for anything structured that downstream code depends on. It's the only one that catches a malformed response instead of passing it along.

**`StructuredOutputParser`** for a flat set of string fields with no dependency on pydantic.

**`JsonOutputParser`** when the shape is genuinely unknown ahead of time.

---

## Parsers vs `with_structured_output`

Both produce structured data, by different mechanisms:

| | Output parsers | `with_structured_output()` |
|---|---|---|
| How | Instructions in the prompt, then parse the text | Provider's tool-calling API |
| Reliability | Model may ignore the format | Constrained at generation |
| Model support | **Any model** | Tool-calling models only |

`with_structured_output()` is more reliable where it's available, because the schema is enforced during decoding rather than requested politely. Parsers work everywhere — including with open models on the Hugging Face endpoint used throughout this repo, which is exactly why they're the right tool here.

---

## How the chain operator works

`|` builds a `RunnableSequence`. Prompts, models and parsers all implement the `Runnable` interface, so each one's output becomes the next one's input:

```
{'topic': 'black hole'}
    ↓ template1     → PromptValue
    ↓ model         → AIMessage
    ↓ parser        → str
    ↓ template2     → PromptValue   (single-variable shortcut)
    ↓ model         → AIMessage
    ↓ parser        → str
```

Everything a chain gains — `.batch()`, `.stream()`, async, LangSmith tracing — comes from that shared interface, not from anything the individual steps do.

---

## Known issues

Verified against `pydantic` 2.13.4 and `langchain-core` 1.5.3.

**1. `city` in `pydantic_outputpasers.py` uses `Field` wrong.**

```python
city: str = Field('Name of the city the person belongs to ')
```

`Field`'s first positional argument is **`default`**, not `description`. That string is being set as the field's default value. Inspecting the model:

```
name | required: True  | default: PydanticUndefined | desc: 'name of the person'
age  | required: True  | default: PydanticUndefined | desc: 'Age of the person'
city | required: False | default: 'Name of the city the person belongs to ' | desc: None
```

Two consequences. The model receives **no description** for `city`, so it gets less guidance than the other two fields. And `city` is now optional — if the model omits it, you get:

```
Person(name='X', age=30, city='Name of the city the person belongs to ')
```

A field whose value is its own description, sitting in your data looking like a real answer. Fix:

```python
city: str = Field(description='Name of the city the person belongs to')
```

**2. `input_varibales` is misspelled in `jsonoutputparser.py`.** Pydantic ignores unrecognised keyword arguments, so it doesn't raise:

```
typo accepted. input_variables = []
```

It happens to be harmless here — the template has no variables besides the partial, so the inferred empty list is correct anyway. But the same typo on a template that *does* have variables would silently misconfigure it. Worth fixing so the pattern in the file is right.

**3. `requirements.txt` doesn't list `pydantic`.** `pydantic_outputpasers.py` imports `BaseModel` and `Field` directly. It works today because langchain pulls pydantic in transitively, but a direct import belongs in the requirements file:

```
langchain
langchain-core
langchain-huggingface
huggingface-hub
pydantic
python-dotenv
```

**4. Filename typo.** `pydantic_outputpasers.py` → `pydantic_outputparsers.py`.

**5. Meta-Llama is a gated model.** `meta-llama/Llama-3.1-8B-Instruct` requires accepting Meta's licence on the model page while signed in, before your token can access it. Without that, every script here returns a 403 — which looks like a broken token rather than a permissions issue. Worth knowing before you debug the wrong thing.

**6. `task="text-generation"` with `ChatHuggingFace`.** Recent `langchain-huggingface` versions expect `task="conversational"` when wrapping an endpoint for chat use. If you hit a task-mismatch error, that's the change.
