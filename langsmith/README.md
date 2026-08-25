# LangChain / LangGraph Playground

Small, self-contained scripts covering LCEL chains, RAG, tool-calling agents, and LangGraph workflows — all running on **Groq** (`openai/gpt-oss-120b`) with LangSmith tracing.

## Files

| File | What it does |
|---|---|
| `simple_llm_call.py` | Minimal LCEL chain: `PromptTemplate → ChatGroq → StrOutputParser` |
| `sequential_chain.py` | Two-stage chain — generate a report on a topic, then summarize it into 5 points |
| `rag_v1.py` | PDF RAG: PyPDFLoader → recursive chunking → HuggingFace embeddings → FAISS → retrieval chain |
| `RAG_V2.PY` | Same pipeline, with setup steps wrapped in `@traceable` so loading/splitting/indexing show as spans in LangSmith |
| `agents.py` | Tool-calling agent with DuckDuckGo search + a WeatherStack weather tool |
| `langraph.py` | LangGraph fan-out/join: three parallel essay evaluators (language, analysis, clarity) merging into a final summary + average score |
| `requirements.txt` | Pinned dependencies |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env`:

```env
GROQ_API_KEY=your_groq_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
WEATHERSTACK_API_KEY=your_weatherstack_key
```

The RAG scripts expect `islr.pdf` in the repo root — change `PDF_PATH` for any other file.

## Run

```bash
python simple_llm_call.py
python sequential_chain.py
python rag_v1.py          # prompts for a question
python RAG_V2.PY          # prompts for a question
python agents.py
python langraph.py
```

## Concepts by file

- **LCEL piping** — `simple_llm_call.py`, `sequential_chain.py`
- **Retrieval** — `RunnableParallel` splits the input into a retrieved-context branch and a passthrough question branch (`rag_v1.py`)
- **Tracing** — `@traceable` decorators plus per-invoke `run_name` / `tags` / `metadata` (`RAG_V2.PY`, `langraph.py`)
- **Structured output** — Pydantic `EvaluationSchema` via `with_structured_output` (`langraph.py`)
- **State reducers** — `Annotated[List[int], operator.add]` lets parallel nodes append scores without clobbering each other (`langraph.py`)

## Notes

- `agents.py` has the WeatherStack key hardcoded in the URL — move it to `.env` and read via `os.getenv` before pushing anywhere public.
- `individual_scores` is typed `List[int]` but the schema returns `float`; harmless at runtime, worth fixing to `List[float]`.
- FAISS index is rebuilt on every run. For a large PDF, `vs.save_local(...)` / `FAISS.load_local(...)` will save you the re-embedding time.
