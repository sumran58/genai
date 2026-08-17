# LangChain — Agents

A working agent on LangChain 1.x: `create_agent` with a Groq-hosted model and a web search tool. The model decides when to search, runs the loop itself, and returns a cited answer.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.x-1C3C3C?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-F55036?logo=groq&logoColor=white)

---

> ### Before committing
>
> A Groq API key is hardcoded in the first cell. **Strip it before the first `git add`** — once a key lands in a commit, deleting it later doesn't remove it from history. See [Fixing the key](#fixing-the-key).

---

## Contents

- [What an agent is](#what-an-agent-is)
- [Fixing the key](#fixing-the-key)
- [Setup](#setup)
- [Walkthrough](#walkthrough)
- [Reading the result](#reading-the-result)
- [Why two langchain packages](#why-two-langchain-packages)
- [Known issues](#known-issues)
- [Where to take it next](#where-to-take-it-next)

---

## What an agent is

A chain is a fixed pipeline — you write the steps and they run in that order every time.

An agent decides for itself. It gets a goal and a set of tools, then loops: consider what's needed, call a tool, read the result, decide whether it's done. The control flow is generated at runtime by the model.

The query here is:

> *what is the population of the capital of france*

Two hops. The model has to establish that the capital is Paris, then find Paris's population. Nothing in the code specifies that sequence — no branching, no ordering logic. The agent works it out and stops when it has enough.

---

## Fixing the key

Replace the first cell:

```python
import os
os.environ["GROQ_API_KEY"] = "gsk_..."      # ← delete this
```

with Colab's Secrets (the key icon in the left sidebar):

```python
import os
from google.colab import userdata
os.environ["GROQ_API_KEY"] = userdata.get('GROQ_API_KEY')
```

Locally, use the `.env` + `python-dotenv` pattern from your other LangChain repos:

```python
from dotenv import load_dotenv
load_dotenv()          # ChatGroq picks up GROQ_API_KEY automatically
```

Also clear saved outputs before committing (**Edit → Clear all outputs**). The current outputs contain no secrets, but they do carry a full token-usage dump and search results — noise in a diff, and a good default habit for notebooks.

---

## Setup

```bash
pip install -q langchain-groq langchain-community langchain-core requests duckduckgo-search
pip install -U ddgs
pip install -U langchain-classic
```

Only one key needed — Groq, free at [console.groq.com](https://console.groq.com). DuckDuckGo search requires none.

Running an agent on Groq's free tier is the main practical advantage of this setup over an OpenAI equivalent. Agents make one model call **per loop iteration** with a conversation that grows each time, so a paid API adds up fast while you're experimenting.

---

## Walkthrough

### The search tool

```python
from langchain_community.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
results = search_tool.invoke('top news in india')
```

Invoked directly first, before any model is involved. Worth doing — it makes clear that a tool is just an object with `.invoke()`, and it confirms search works before you start debugging the agent.

### The model

```python
llm = ChatGroq(model="openai/gpt-oss-120b")
llm.invoke('hi')
```

Another isolated smoke test. Two independent pieces verified separately, then combined — the right order for debugging anything with several moving parts.

The response metadata in the saved output is worth reading:

```
'reasoning_content': 'We need to respond as ChatGPT. The user says "hi"...'
'completion_tokens_details': {'reasoning_tokens': 35}
```

`gpt-oss-120b` is a **reasoning model** — it generates internal reasoning tokens before its visible answer. Here, 35 of 53 completion tokens were reasoning. That's usually good for agent work, since tool selection benefits from deliberation, but it means token counts run higher than the visible output suggests.

### The agent

```python
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[search_tool],
    system_prompt="You are a helpful assistant. Use the search tool whenever current information is required."
)
```

Three arguments and the agent is done. `create_agent` returns a compiled LangGraph graph with the tool-calling loop already built in — no separate executor to construct and wire up.

Under the hood it uses the provider's **native tool calling**: the tool schema goes to the API, and the model returns a structured call request. That's more reliable than the older ReAct approach, which asked the model to write `Thought:/Action:` text that then had to be parsed — and broke whenever the model drifted from the format.

The system prompt is doing real work. *"Use the search tool whenever current information is required"* is what pushes the model to search rather than answer from memory. Without it, a model that thinks it knows the answer will often skip the tool.

### Invoking

```python
response = agent.invoke({
    "messages": [{"role": "user", "content": "what is the population of the capital of france"}]
})
print(response["messages"][-1].content)
```

Input and output are both **message lists**, not a plain string. `response["messages"]` holds the whole exchange — user message, tool calls, tool results, final answer — so `[-1]` is the last message.

Print the full list once. Seeing the intermediate tool-call and tool-result messages is the clearest picture of what the agent actually did:

```python
for m in response["messages"]:
    m.pretty_print()
```

---

## Reading the result

```
The capital of France, **Paris**, had an estimated **population of 2,102,650**
within its administrative city limits as of **January 2023**【2†L1-L3】.

*(For context, the larger Paris urban area is much bigger—over 10 million
people—but the figure above refers to the city proper.)*
```

Three things worth noticing.

**It resolved the two hops.** The question never says "Paris." The model had to establish the capital, then look up its population, in one pass.

**It disambiguated.** City proper versus urban area is exactly the trap in this question — 2.1 million and 10 million are both correct answers to differently-scoped versions of it. The model picked one, said which, and noted the other.

**`【2†L1-L3】` is a citation marker**, pointing at a line range in the search result. Useful for tracing an answer back to its source, though the format is a model-specific artefact rather than a LangChain feature.

---

## Why two langchain packages

```python
from langchain.agents import create_agent      # langchain 1.x
from langchain_classic import hub              # langchain-classic
```

LangChain 1.0 was a breaking rewrite. `AgentExecutor`, `create_react_agent`, `LLMChain` and other pre-1.0 APIs were removed from the main package and moved to **`langchain-classic`**, which exists so old code keeps running.

`hub` is one of those relocated pieces. It's imported here but not used — the older ReAct approach needed a Hub-pulled prompt to define the `Thought:/Action:` format, whereas `create_agent` needs only a system prompt string. See [Known issues](#known-issues) item 2.

Quick orientation if you hit an import error in older tutorial code:

| Old API | Status in 1.x |
|---|---|
| `AgentExecutor` | Moved to `langchain-classic` |
| `create_react_agent` | Moved to `langchain-classic` |
| `LLMChain` | Moved to `langchain-classic` |
| `create_agent` | **New, in `langchain.agents`** |

---

