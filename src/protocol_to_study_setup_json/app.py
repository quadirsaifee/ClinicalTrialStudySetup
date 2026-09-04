"""Application entry point for the study setup generator."""

from __future__ import annotations

import json
from pathlib import Path

from .agent import ProtocolStudySetupAgent
from .loader import ProtocolDocumentLoader


def main() -> None:
    """Load sample protocol files, extract their text, and run the Azure-backed extraction flow."""
    sample_folder = Path(__file__).resolve().parents[2] / "Protocol documents"
    loader = ProtocolDocumentLoader()
    documents = loader.load_from_folder(sample_folder)
    combined = loader.combine_text(documents)

    print(f"Loaded {len(documents)} documents from {sample_folder}")
    print("First 500 chars of extracted text:")
    print(combined[:500])

    try:
        agent = ProtocolStudySetupAgent()
        result = agent.run(sample_folder)
        output_file = Path(__file__).resolve().parents[2] / "studySetupJSON" / "study_setup_output.txt"
        print(f"Saved agent output to {output_file}")
        print(json.dumps(result, indent=2))
    except Exception as exc:  # pragma: no cover - CLI behavior
        print(f"Azure model configuration is missing or the model call failed: {exc}")
        print("Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and AZURE_OPENAI_MODEL_NAME before running the agent.")


if __name__ == "__main__":
    main()
