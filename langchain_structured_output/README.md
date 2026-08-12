# LangChain — Structured Output

Getting an LLM to return parseable data instead of prose. Three ways to declare a schema — `TypedDict`, Pydantic, and raw JSON Schema — with the trade-offs between them.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=white)

---

## Contents

- [The problem](#the-problem)
- [Setup](#setup)
- [Foundations](#foundations)
- [The three approaches](#the-three-approaches)
- [Which one to use](#which-one-to-use)
- [How it works underneath](#how-it-works-underneath)
- [Known issues](#known-issues)

---

## The problem

A model asked to analyse a product review returns paragraphs. Useful to read, useless to a program — you can't put it in a database, filter it, or count sentiments across ten thousand reviews.

`with_structured_output()` fixes that. You hand it a schema, and the model returns an object matching that shape:

```python
structured_model = model.with_structured_output(Review)
result = structured_model.invoke(review_text)
# {'summary': '...', 'sentiment': 'neg', 'pros': [...], 'cons': [...]}
```

The interesting part is that the schema does double duty. It tells the model what to produce *and* it validates what came back. These scripts work through what you get from each way of writing one.

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

> Check `.env` is in `.gitignore` before the first commit. A key that reaches GitHub is compromised, and removing it later doesn't clear it from history.

Free key at [console.groq.com](https://console.groq.com).

---

## Foundations

Two scripts with no LLM in them, establishing what the schema types actually do.

### `typedict_demo.py` — TypedDict

```python
class Person(TypedDict):
    name: str
    age: int

new_person: Person = {'name': 'Simran', "age": 22}
```

A `TypedDict` is a dict with type hints attached. It is **hints only** — nothing is checked at runtime. Assigning `age` a string here raises no error; Python builds the dict regardless. The annotations exist for your editor and for type checkers like mypy.

That matters for the LLM case: a `TypedDict` schema tells the model what shape to produce, but if the model returns something else, nothing catches it.

### `pydantic_demo.py` — Pydantic

```python
class Student(BaseModel):
    name: str = 'Sim'
    age: Optional[int] = None
    email: EmailStr
    cgpa: float = Field(ge=0, le=10)

new_student = {'age': '32', 'email': 'simhar67@gmail.com', 'cgpa': 10}
student = Student(**new_student)
```

Pydantic enforces at runtime. Four distinct behaviours in those four lines:

**Defaults.** `name` isn't in the input dict, so it becomes `'Sim'`.

**Optional.** `Optional[int] = None` means the field may be absent or explicitly null. Note that `Optional[int]` alone doesn't make a field optional — the `= None` default does. Without it the field is still required, just allowed to hold `None`.

**Type coercion.** `age` comes in as the string `'32'` and lands as the integer `32`. Pydantic converts when the conversion is unambiguous rather than rejecting. Verified:

```
name='Sim' age=32 cgpa=10.0 | age type: int
```

**Constraints.** `Field(ge=0, le=10)` bounds `cgpa`. A value of `11` raises `ValidationError` naming the field and the rule it broke. And because `Field()` is given no default, `cgpa` stays **required** — `Field(...)` with the explicit ellipsis is clearer about that intent, but both behave the same.

`EmailStr` goes further and validates the address format. It needs an extra dependency — see [Known issues](#known-issues) item 1.

---

## The three approaches

### `structured_output_typedict.py`

```python
class Review(TypedDict):
    summary: str
    sentiment: str

structured_model = model.with_structured_output(Review)
result = structured_model.invoke("the hardware is great but the software feels bloated...")
```

Minimal. Two fields, no descriptions.

The comment in the file makes the key observation: nothing here tells the model *what* a summary or a sentiment is. LangChain converts the `TypedDict` into a schema and passes it to the API as a tool definition, and the model infers meaning from the field names alone.

That inference is fragile. `sentiment: str` invites `"negative"`, `"Negative"`, `"mixed"`, or a whole sentence — any of them satisfies "a string". The fix hinted at in the comments:

```python
from typing import Annotated
class Review(TypedDict):
    summary: Annotated[str, "generate the summary from the review"]
```

`Annotated` attaches a description that reaches the model. Worth doing for every field.

Returns a plain `dict`. Nothing validates it.

### `structured_output_pydantic.py`

```python
class Review(BaseModel):
    key_themes: list[str] = Field(description="Write down all the key themes discussed in the review in a list")
    summary: str = Field(description="A brief summary of the review")
    sentiment: Literal["pos", "neg"] = Field(description="...")
    pros: Optional[list[str]] = Field(default=None, description="...")
    cons: Optional[list[str]] = Field(default=None, description="...")
    name: Optional[str] = Field(default=None, description="Write the name of the reviewer")
```

The same idea with every gap closed.

`Field(description=...)` on each field is the instruction the model actually reads — these strings end up in the schema sent to the API, so they function as per-field prompts.

`Literal["pos", "neg"]` is the important upgrade over `sentiment: str`. It constrains the output to two exact values, so downstream code can rely on them without normalising case or synonyms.

`Optional[...] = None` on `pros`, `cons` and `name` marks them genuinely optional. A review with no complaints returns `cons=None` rather than the model inventing something to fill the slot.

Returns a validated `Review` **object**, so `result.sentiment` works with editor autocomplete, and a response that doesn't match the schema raises rather than flowing downstream.

### `structured_output_json.py`

The same schema written as a raw JSON Schema dict — `"type": "object"`, `"properties"`, `"required"`, `"enum"` in place of `Literal`, `"type": ["array", "null"]` in place of `Optional`.

This is what the other two get compiled into. Writing it by hand is more verbose and gives up validation — you get a plain dict back — but it's language-independent. A schema in a `.json` file can be shared with a TypeScript or Go service, which a Python class can't.

---

## Which one to use

| | TypedDict | Pydantic | JSON Schema |
|---|---|---|---|
| Runtime validation | No | **Yes** | No |
| Type coercion | No | **Yes** | No |
| Defaults | No | **Yes** | No |
| Field constraints (`ge`, `le`, regex) | No | **Yes** | Partial |
| Returns | `dict` | **Object** | `dict` |
| Cross-language | No | No | **Yes** |
| Extra dependency | No | Yes | No |

**Default to Pydantic.** It's the only option that verifies the model actually returned what you asked for, and the one you already know from FastAPI — the same `BaseModel` and `Field` work in both places.

**TypedDict** when you want zero dependencies and the shape is trivial.

**JSON Schema** when the schema has to be shared across languages or loaded from a config file.

---

## How it works underneath

`with_structured_output()` doesn't ask nicely in the prompt and hope. It uses the provider's **tool calling** API.

The schema is converted to a tool definition and sent alongside the prompt. The API constrains generation so the output conforms — for many providers this is enforced at the decoding level, meaning tokens that would break the schema simply aren't sampled. That's why it's far more reliable than "reply in JSON" in a system prompt, which fails whenever the model wraps its answer in prose or a markdown fence.

Two consequences worth knowing:

- **It only works on models that support tool calling.** A base completion model will fail here. `llama-3.3-70b-versatile` on Groq supports it.
- **Field names and descriptions are prompt text.** They're the only instruction the model gets about each field, so `key_themes` with a clear description behaves very differently from `kt` with none.

---

## Known issues

Verified against `pydantic` 2.13.4.

**1. `EmailStr` needs a dependency that isn't installed.** `pydantic_demo.py` imports `EmailStr`, which requires the `email-validator` package. On a fresh clone it fails:

```
ImportError: email-validator is not installed, run `pip install 'pydantic[email]'`
```

`requirements.txt` also never lists `pydantic` itself — it arrives only as a transitive dependency of langchain, which works today but shouldn't be relied on for something you import directly. The file should be:

```
langchain
langchain-core
langchain-groq
pydantic[email]
python-dotenv
```

**2. `json_schema.json` is not a valid JSON Schema.** Property values must be schema *objects*, not bare type strings:

```json
"properties": {
    "name": "string",      ← wrong
    "age": "integer"
}
```

Running it through a validator confirms it:

```
schema INVALID: 'integer' is not of type 'object', 'boolean'
```

Correct form:

```json
"properties": {
    "name": {"type": "string"},
    "age":  {"type": "integer"}
}
```

The file is currently unused — `structured_output_json.py` defines its schema inline — so nothing breaks today. But it's the reference example for the JSON Schema approach, and as written it teaches the wrong shape. Compare it against the inline schema in `structured_output_json.py`, which is correct.

**3. The sentiment enum and its description disagree.** Both the Pydantic and JSON versions constrain sentiment to two values while describing three:

```python
sentiment: Literal["pos", "neg"] = Field(
    description="Return sentiment of the review either negative, positive or neutral"
)
```

The constraint wins — `"neutral"` can't be produced. But the model is reading a description that offers an option it isn't allowed to pick, which is exactly the kind of contradiction that produces erratic behaviour on genuinely mixed reviews. Either drop "neutral" from the description or add it to the `Literal`.

**4. `pydantic_demo.py` was uploaded twice.** Only one copy is needed in the repo.

**5. `structured_output_typedict.py` doesn't use `Annotated`.** The commented-out block at the bottom shows the right pattern. Applying it turns a demo that relies on lucky field-name inference into one that actually instructs the model — worth uncommenting so the file demonstrates the fix rather than just mentioning it.
