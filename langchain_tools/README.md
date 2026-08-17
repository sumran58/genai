# LangChain — Tools

Every way to give an LLM something it can actually *do*. Built-in tools, the `@tool` decorator, `StructuredTool`, `BaseTool`, and toolkits — worked through in one notebook.

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)

---

## Contents

- [What a tool is](#what-a-tool-is)
- [Setup](#setup)
- [Built-in tools](#built-in-tools)
- [The four ways to build one](#the-four-ways-to-build-one)
- [Toolkits](#toolkits)
- [Which approach to use](#which-approach-to-use)
- [Known issues](#known-issues)

---

## What a tool is

An LLM can only produce text. It can't search the web, run a shell command, or reliably multiply two large numbers. A **tool** closes that gap: a Python function wrapped so the model can request it be called.

The critical insight is that the model never executes anything. It reads the tool's **name, description, and argument schema**, decides one is relevant, and emits a structured request like `multiply(a=7, b=12)`. Your code runs the function and hands back the result.

That makes the metadata the entire interface. Name, docstring and type hints aren't documentation here — they're the prompt the model reads to decide what to call and how. A vague description produces a tool the model never picks, or picks wrongly.

---

## Setup

```bash
pip install langchain langchain-core langchain-community duckduckgo-search langchain_experimental pydantic
pip install -U ddgs
```

Both install cells are at the top of the notebook, so it runs as-is in Colab.

The second one matters: `duckduckgo-search` was renamed to `ddgs`, and older versions of the search tool raise a `RuntimeError` telling you to install the new package. Installing both covers either case.

Nothing here needs an API key — every example runs locally or against a free search endpoint. That's unusual for LangChain material and makes this notebook cheap to re-run while experimenting.

---

## Built-in tools

### `DuckDuckGoSearchRun`

```python
from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
results = search_tool.invoke('ipl news')
```

Web search, no API key. Gives a model access to information past its training cutoff.

### `ShellTool`

```python
from langchain_community.tools import ShellTool
shell_tool = ShellTool()
results = shell_tool.invoke('pwd')
```

Runs shell commands. Powerful and genuinely dangerous — a model deciding what to execute on your machine is a real risk, and prompt injection in retrieved content can drive that decision. Fine in a disposable Colab runtime, which is where this notebook lives. Not something to attach to an agent on your own machine without a command allowlist.

Note that both are invoked directly here. That's deliberate — it shows a tool is just an object with `.invoke()`, before any model is involved.

---

## The four ways to build one

### 1. `@tool` decorator

The notebook builds this in three visible steps, which is the clearest part of the whole file.

**Step 1** — a plain function:

```python
def multiply(a, b):
    """multiply two numbers"""
    return a * b
```

**Step 2** — add type hints:

```python
def multiply(a: int, b: int) -> int:
    """multiply two numbers"""
    return a * b
```

**Step 3** — decorate:

```python
@tool
def multiply(a: int, b: int) -> int:
    """multiply two numbers"""
    return a * b
```

The type hints stop being optional at step 3. LangChain reads them to build the JSON schema the model receives; without them there's no argument specification and the model is guessing. The docstring becomes the tool's description — the text the model uses to decide whether this tool is relevant.

Tools are Runnables, so they invoke like anything else:

```python
multiply.invoke({"a": 2, "b": 3})   # 6
```

And they expose what the model will see:

```python
print(multiply.name)          # multiply
print(multiply.description)   # multiply two numbers
print(multiply.args)          # {'a': {'title': 'A', 'type': 'integer'}, ...}
```

Printing `.args` is the habit worth keeping. It's the actual contract with the model, and it's how you catch a schema that didn't get applied — which is exactly what happens in the next section.

### 2. `StructuredTool`

```python
class MultiplyInput(BaseModel):
    a: int = Field(description="the first number to add")
    b: int = Field(description="the second number to add")

multiply_tool = StructuredTool.from_function(
    func=multiply_fun,
    name="multiply",
    description="multiply the two numbers",
    args_schema=MultiplyInput
)
```

Same idea, but the argument schema is a separate Pydantic model instead of being inferred from hints.

What that buys you is **per-argument descriptions**. With `@tool` the model gets types only; here each field carries its own explanation. For a tool with several similar-looking arguments, that's the difference between the model filling them correctly and swapping them.

You also get Pydantic validation — constraints like `ge`, `le`, and regex patterns apply to the model's arguments before your function runs.

The notebook's version has a typo that silently disables all of this — see [Known issues](#known-issues) item 1.

### 3. `BaseTool`

```python
class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "Multiply two numbers"
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, a: int, b: int) -> int:
        return a * b
```

The abstract base class both `@tool` and `StructuredTool` inherit from, as the notebook comment correctly notes.

Subclassing gives you full control: state in `__init__`, an async `_arun`, custom error handling, overridden schema generation. The cost is verbosity for what the decorator does in four lines.

Reach for it when a tool needs to hold something — a database connection, an API client, a cache — rather than being a pure function.

### 4. Toolkits

```python
class MathToolkit:
    def get_tools(self):
        return [add, multiply]

toolkit = MathToolkit()
tools = toolkit.get_tools()
```

A toolkit groups related tools behind one object, so an agent gets a coherent set in a single call instead of a hand-assembled list. LangChain ships many — SQL, file system, GitHub — all following this `get_tools()` shape.

The final cell in the notebook shadows the `tool` decorator; see [Known issues](#known-issues) item 2.

---

## Which approach to use

| | `@tool` | `StructuredTool` | `BaseTool` |
|---|---|---|---|
| Lines of code | **Fewest** | Medium | Most |
| Per-argument descriptions | No | **Yes** | **Yes** |
| Pydantic validation | Basic | **Yes** | **Yes** |
| Can hold state | No | No | **Yes** |
| Async support | Via decorator | Via `coroutine=` | **`_arun`** |

**`@tool`** for almost everything. Simple functions with clear names and a good docstring.

**`StructuredTool`** when arguments need individual explanation or validation constraints.

**`BaseTool`** when the tool needs state or custom lifecycle behaviour.

---

