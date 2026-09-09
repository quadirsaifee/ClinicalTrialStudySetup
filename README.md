# ProtocoltoStudySetupJSON

Agentic clinical trial protocol processing app that converts protocol documentation and digital trial inputs into a structured JSON study setup.

## Stack

- Python 3.11+
- LangChain
- LangGraph
- Pydantic v2
- OpenAI-compatible LLMs

## Goal

Generate a JSON object for study configuration that includes:

- study sites
- visits
- cohorts
- tests and assessments
- kits and materials
- protocol-derived scheduling details

## Project structure

```text
ProtocoltoStudySetupJSON/
├── src/
│   └── protocol_to_study_setup_json/
│       ├── __init__.py
│       ├── app.py
│       └── models.py
├── tests/
│   └── test_models.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── requirements.txt
└── .venv/
```

## Quick start

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

python -m pip install -U pip
python -m pip install -e .
```

If you are running directly from the repository without the package installed, set the Python path to include the `src` folder before starting Uvicorn:

```bash
# Windows cmd
set PYTHONPATH=src

# Windows PowerShell
$env:PYTHONPATH = "src"
```

## Run the FastAPI application

Start the API from the project root:

```bash
python -m uvicorn protocol_to_study_setup_json.api:app --reload
```

Important: the app target is `protocol_to_study_setup_json.api:app` and not `:ap`.

Open the interactive API documentation at http://127.0.0.1:8000/docs.
Use `POST /agent` with `{}` to process the default `Protocol documents` folder.

## Pydantic JSON schema

The package includes typed domain models that can be used to validate and serialize protocol-derived study setup JSON.

```python
from protocol_to_study_setup_json.models import StudySetup

schema = StudySetup.model_json_schema()
```
