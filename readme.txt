ProtocoltoStudySetupJSON

Quick start:

1) Create a virtual environment
   python -m venv .venv

   Linux/macOS:
   source .venv/bin/activate

   Windows PowerShell:
   .\.venv\Scripts\Activate.ps1

2) Install dependencies
   python -m pip install -U pip
   python -m pip install -e .

3) Run the FastAPI app from the project root
   python -m uvicorn protocol_to_study_setup_json.api:app --reload

Important:
- Use the correct app target: protocol_to_study_setup_json.api:app
- Do not use :ap
- If Python cannot import the package, set PYTHONPATH to the src folder:

  Windows cmd:
  set PYTHONPATH=src

  Windows PowerShell:
  $env:PYTHONPATH = "src"

Open the docs at:
http://127.0.0.1:8000/docs
