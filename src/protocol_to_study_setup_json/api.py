"""FastAPI interface for protocol-to-study-setup generation."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .agent import ProtocolStudySetupAgent


class AgentRequest(BaseModel):
    input_folder: str = Field(default="Protocol documents", min_length=1)


app = FastAPI(
    title="Protocol to Study Setup API",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent")
def invoke_agent(request: AgentRequest) -> dict:
    input_folder = Path(request.input_folder)
    if not input_folder.exists():
        raise HTTPException(status_code=404, detail=f"Input folder does not exist: {input_folder}")
    if not input_folder.is_dir():
        raise HTTPException(status_code=400, detail=f"Expected a folder, got: {input_folder}")

    try:
        return ProtocolStudySetupAgent().run(input_folder)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - protects API callers from model errors
        raise HTTPException(status_code=502, detail=f"Agent invocation failed: {exc}") from exc