from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.tools import tool

try:
    from langchain_openai import AzureChatOpenAI
except ImportError:  # pragma: no cover - optional dependency for real model calls
    AzureChatOpenAI = None

try:
    from langchain.agents import create_deep_agent
except ImportError:  # pragma: no cover - compatibility for older LangChain versions
    try:
        from langchain.agents import create_agent as create_deep_agent
    except ImportError:
        create_deep_agent = None

from .loader import ProtocolDocumentLoader

load_dotenv()

MOCK_CLINICAL_TRIAL_JSON = {
    "clinical_trial_setup": {
        "protocol_identification": {
            "protocol_id": "PRO-2026-NEURO-042",
            "nct_number": "NCT09876543",
            "official_title": "A Phase III, Randomized, Double-Blind, Placebo-Controlled Study to Evaluate the Efficacy and Safety of NeuroX in Patients with Early-Stage Alzheimer's Disease",
            "brief_title": "NeuroX Efficacy and Safety Study in Early Alzheimer's",
            "phase": "Phase 3",
            "sponsor": {
                "name": "Nexus Therapeutics Inc.",
                "type": "Industry",
                "lead_sponsor": True,
            },
        },
        "study_design": {
            "allocation": "Randomized",
            "intervention_model": "Parallel Assignment",
            "masking": "Double-blind",
            "masking_roles": [
                "Participant",
                "Care Provider",
                "Investigator",
                "Outcomes Assessor",
            ],
            "primary_purpose": "Treatment",
            "target_enrollment": 450,
        },
        "eligibility_criteria": {
            "minimum_age": "50 Years",
            "maximum_age": "85 Years",
            "sex": "All",
            "inclusion_criteria": [
                "Diagnosis of early-stage Alzheimer's disease according to NIA-AA criteria.",
                "MMSE score between 20 and 26 inclusive at the time of screening.",
                "Patient has a reliable caregiver who accompanies them to study visits.",
            ],
            "exclusion_criteria": [
                "History of significant central nervous system vascular disease.",
                "Current use of any other investigational drug or device within 30 days of screening.",
                "Known hypersensitivity to NeuroX or its excipients.",
            ],
        },
        "study_arms": [
            {
                "arm_id": "ARM-001",
                "label": "NeuroX High Dose",
                "type": "Experimental",
                "description": "Participants receive NeuroX 10mg orally once daily for 24 weeks.",
                "interventions": [
                    {"type": "Drug", "name": "NeuroX", "description": "10mg tablet"}
                ],
            },
            {
                "arm_id": "ARM-002",
                "label": "Placebo Control",
                "type": "Placebo Comparator",
                "description": "Participants receive matching placebo tablet orally once daily for 24 weeks.",
                "interventions": [
                    {"type": "Drug", "name": "Placebo", "description": "Matching inert tablet"}
                ],
            },
        ],
        "laboratory_tests": [
            {
                "panel_id": "LAB-HEM-01",
                "panel_name": "Safety Hematology",
                "analytes": [
                    {"code": "WBC", "name": "White Blood Cell Count", "unit": "10^3/uL", "method": "Automated Cell Counter"},
                    {"code": "RBC", "name": "Red Blood Cell Count", "unit": "10^6/uL", "method": "Automated Cell Counter"},
                    {"code": "HGB", "name": "Hemoglobin", "unit": "g/dL", "method": "Spectrophotometry"},
                    {"code": "PLT", "name": "Platelets", "unit": "10^3/uL", "method": "Electrical Impedance"},
                ],
            },
            {
                "panel_id": "LAB-CHM-02",
                "panel_name": "Safety Chemistry",
                "analytes": [
                    {"code": "ALT", "name": "Alanine Aminotransferase", "unit": "U/L", "method": "Enzymatic"},
                    {"code": "AST", "name": "Aspartate Aminotransferase", "unit": "U/L", "method": "Enzymatic"},
                    {"code": "CREAT", "name": "Serum Creatinine", "unit": "mg/dL", "method": "Jaffe Method"},
                    {"code": "GLU", "name": "Fasting Plasma Glucose", "unit": "mg/dL", "method": "Hexokinase"},
                ],
            },
        ],
        "investigational_kits": [
            {
                "kit_type_id": "KIT-IP-10MG",
                "name": "NeuroX 10mg Treatment Kit",
                "category": "Investigational Product",
                "description": "Contains a 30-day supply of NeuroX 10mg tablets (35 tablets total including overage).",
                "storage_conditions": "Store at 20°C to 25°C (68°F to 77°F); excursions permitted between 15°C and 30°C.",
                "dispensing_unit": "Bottle",
                "blinded": True,
            },
            {
                "kit_type_id": "KIT-PBO-00",
                "name": "Placebo Matching Kit",
                "category": "Placebo",
                "description": "Contains a 30-day supply of matching inert placebo tablets.",
                "storage_conditions": "Store at 20°C to 25°C (68°F to 77°F).",
                "dispensing_unit": "Bottle",
                "blinded": True,
            },
        ],
        "outcome_measures": {
            "primary_outcomes": [
                {
                    "measure": "Change from baseline in the Alzheimer's Disease Assessment Scale–Cognitive Subscale (ADAS-Cog 13)",
                    "time_frame": "Baseline to Week 24",
                    "description": "A 13-item scale used to assess cognitive function. Higher scores indicate greater impairment.",
                }
            ],
            "secondary_outcomes": [
                {
                    "measure": "Incidence of treatment-emergent adverse events (TEAEs)",
                    "time_frame": "Baseline to Week 28 (Safety Follow-up)",
                    "description": "Safety and tolerability assessed by physical exams, laboratory tests, and ECGs.",
                }
            ],
        },
        "schedule_of_events": {
            "visits": [
                {
                    "visit_id": "V1",
                    "name": "Screening",
                    "window": "Day -14 to Day -1",
                    "procedures": [
                        "Informed Consent",
                        "Medical History",
                        "Inclusion/Exclusion Review",
                        "Physical Examination",
                        "Vital Signs",
                        "MMSE Assessment",
                    ],
                    "required_lab_panels": ["LAB-HEM-01", "LAB-CHM-02"],
                    "kits_dispensed": [{"kit_type_id": "KIT-LAB-SCR", "quantity": 1}],
                },
                {
                    "visit_id": "V2",
                    "name": "Baseline / Randomization",
                    "window": "Day 1",
                    "procedures": ["Vital Signs", "ADAS-Cog 13 Baseline", "Randomization"],
                    "required_lab_panels": ["LAB-BIO-03"],
                    "kits_dispensed": [{"comment": "System uses IRT / IWRS to dispense KIT-IP-10MG or KIT-PBO-00 depending on randomized arm", "quantity": 1}],
                },
            ]
        },
    }
}


class ProtocolStudySetupAgent:
    def __init__(self, *, model_name: str | None = None, azure_endpoint: str | None = None):
        self.loader = ProtocolDocumentLoader()
        self.model_name = model_name or os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4o-mini")
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.use_mock_model = bool(os.getenv("USE_MOCK_MODEL", "1")) or not self.azure_endpoint or not self.api_key
        self.model = self._build_model()

    def _build_model(self):
        if self.use_mock_model:
            return None
        if not self.azure_endpoint:
            raise ValueError(
                "AZURE_OPENAI_ENDPOINT is not set. Define it in your environment or pass azure_endpoint=."
            )
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set.")
        if AzureChatOpenAI is None:
            raise ImportError("langchain-openai is required for Azure model calls.")

        return AzureChatOpenAI(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            azure_deployment=self.model_name,
            model=self.model_name,
        )

    def load_input_documents(self, folder: str | Path) -> str:
        docs = self.loader.load_from_folder(folder)
        return self.loader.combine_text(docs)

    def build_prompt(self) -> str:
        return """
You are a clinical trial protocol extraction expert.

Given protocol text from PDF or DOCX files, extract the study information and return only a valid JSON object with this exact structure:
{
  "clinical_trial_setup": {
    "protocol_identification": {
      "protocol_id": "PRO-2026-NEURO-042",
      "nct_number": "NCT09876543",
      "official_title": "...",
      "brief_title": "...",
      "phase": "Phase 3",
      "sponsor": {
        "name": "Nexus Therapeutics Inc.",
        "type": "Industry",
        "lead_sponsor": true
      }
    },
    "study_design": {
      "allocation": "Randomized",
      "intervention_model": "Parallel Assignment",
      "masking": "Double-blind",
      "masking_roles": ["Participant", "Care Provider", "Investigator", "Outcomes Assessor"],
      "primary_purpose": "Treatment",
      "target_enrollment": 450
    },
    "eligibility_criteria": {
      "minimum_age": "50 Years",
      "maximum_age": "85 Years",
      "sex": "All",
      "inclusion_criteria": ["..."],
      "exclusion_criteria": ["..."]
    },
    "study_arms": [
      {
        "arm_id": "ARM-001",
        "label": "NeuroX High Dose",
        "type": "Experimental",
        "description": "...",
        "interventions": [{"type": "Drug", "name": "NeuroX", "description": "10mg tablet"}]
      }
    ],
    "laboratory_tests": [
      {
        "panel_id": "LAB-HEM-01",
        "panel_name": "Safety Hematology",
        "analytes": [{"code": "WBC", "name": "White Blood Cell Count", "unit": "10^3/uL", "method": "Automated Cell Counter"}]
      }
    ],
    "investigational_kits": [
      {
        "kit_type_id": "KIT-IP-10MG",
        "name": "NeuroX 10mg Treatment Kit",
        "category": "Investigational Product",
        "description": "...",
        "storage_conditions": "...",
        "dispensing_unit": "Bottle",
        "blinded": true
      }
    ],
    "outcome_measures": {
      "primary_outcomes": [{"measure": "...", "time_frame": "...", "description": "..."}],
      "secondary_outcomes": [{"measure": "...", "time_frame": "...", "description": "..."}]
    },
    "schedule_of_events": {
      "visits": [{
        "visit_id": "V1",
        "name": "Screening",
        "window": "Day -14 to Day -1",
        "procedures": ["..."],
        "required_lab_panels": ["LAB-HEM-01", "LAB-CHM-02"],
        "kits_dispensed": [{"kit_type_id": "KIT-LAB-SCR", "quantity": 1}]
      }]
    }
  }
}

Rules:
- Return only valid JSON with no markdown fences.
- Use null/empty arrays when value is unknown.
- Do not invent unsupported information.
- Preserve exact field names and nesting.
"""

    def _document_tool(self):
        @tool
        def read_protocol_documents(folder_path: str) -> str:
            """Read all supported protocol files in a folder and return their extracted text."""
            return self.load_input_documents(folder_path)

        return read_protocol_documents

    def create_agent(self):
        if self.use_mock_model:
            return None

        if create_deep_agent is None:
            raise ImportError(
                "This LangChain version does not expose create_deep_agent; install a newer LangChain release "
                "that includes the official deep-agent API."
            )

        try:
            agent = create_deep_agent(
                model=self.model,
                tools=[self._document_tool()],
                instructions=self.build_prompt(),
            )
        except TypeError:
            agent = create_deep_agent(
                model=self.model,
                tools=[self._document_tool()],
                system_message=self.build_prompt(),
            )
        return agent

    def _mock_model_response(self) -> Dict[str, Any]:
        return json.loads(json.dumps(MOCK_CLINICAL_TRIAL_JSON))

    def save_output(self, result: Dict[str, Any]) -> Path:
        output_folder = Path(__file__).resolve().parents[2] / "studySetupJSON"
        output_folder.mkdir(parents=True, exist_ok=True)
        output_file = output_folder / "study_setup_output.txt"
        output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        return output_file

    def run(self, input_folder: str | Path) -> Dict[str, Any]:
        if self.use_mock_model:
            result = self._mock_model_response()
        else:
            agent = self.create_agent()
            response = agent.invoke({"messages": [{"role": "user", "content": f"Read all files in {input_folder} and extract the JSON structure from the protocol documents."}]})
            raw = response["messages"][-1].content if isinstance(response, dict) and "messages" in response else str(response)

            if isinstance(raw, list):
                raw = "".join(part.get("text", "") for part in raw if isinstance(part, dict))

            text = str(raw).strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].lstrip()

            result = json.loads(text)

        self.save_output(result)
        return result
