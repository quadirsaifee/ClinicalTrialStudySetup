from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Sponsor(BaseModel):
    name: str
    type: str
    lead_sponsor: bool = False


class ProtocolIdentification(BaseModel):
    protocol_id: str
    nct_number: Optional[str] = None
    official_title: str
    brief_title: Optional[str] = None
    phase: Optional[str] = None
    sponsor: Sponsor


class StudyDesign(BaseModel):
    allocation: Optional[str] = None
    intervention_model: Optional[str] = None
    masking: Optional[str] = None
    masking_roles: List[str] = Field(default_factory=list)
    primary_purpose: Optional[str] = None
    target_enrollment: Optional[int] = None


class EligibilityCriteria(BaseModel):
    minimum_age: Optional[str] = None
    maximum_age: Optional[str] = None
    sex: Optional[str] = None
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)


class Intervention(BaseModel):
    type: str
    name: str
    description: Optional[str] = None


class StudyArm(BaseModel):
    arm_id: str
    label: str
    type: str
    description: Optional[str] = None
    interventions: List[Intervention] = Field(default_factory=list)


class LabAnalyte(BaseModel):
    code: str
    name: str
    unit: Optional[str] = None
    method: Optional[str] = None


class LaboratoryTest(BaseModel):
    panel_id: str
    panel_name: str
    analytes: List[LabAnalyte] = Field(default_factory=list)


class InvestigationalKit(BaseModel):
    kit_type_id: str
    name: str
    category: str
    description: Optional[str] = None
    storage_conditions: Optional[str] = None
    dispensing_unit: Optional[str] = None
    blinded: bool = False


class Outcome(BaseModel):
    measure: str
    time_frame: Optional[str] = None
    description: Optional[str] = None


class OutcomeMeasures(BaseModel):
    primary_outcomes: List[Outcome] = Field(default_factory=list)
    secondary_outcomes: List[Outcome] = Field(default_factory=list)


class KitsDispensed(BaseModel):
    kit_type_id: Optional[str] = None
    quantity: Optional[int] = None
    comment: Optional[str] = None


class VisitEvent(BaseModel):
    visit_id: str
    name: str
    window: Optional[str] = None
    procedures: List[str] = Field(default_factory=list)
    required_lab_panels: List[str] = Field(default_factory=list)
    kits_dispensed: List[KitsDispensed] = Field(default_factory=list)


class ScheduleOfEvents(BaseModel):
    visits: List[VisitEvent] = Field(default_factory=list)


class ClinicalTrialSetupRoot(BaseModel):
    protocol_identification: ProtocolIdentification
    study_design: StudyDesign
    eligibility_criteria: EligibilityCriteria
    study_arms: List[StudyArm] = Field(default_factory=list)
    laboratory_tests: List[LaboratoryTest] = Field(default_factory=list)
    investigational_kits: List[InvestigationalKit] = Field(default_factory=list)
    outcome_measures: OutcomeMeasures
    schedule_of_events: ScheduleOfEvents


class ClinicalTrialSetup(BaseModel):
    clinical_trial_setup: ClinicalTrialSetupRoot

    model_config = {
        "title": "ClinicalTrialSetup",
        "extra": "forbid",
        "populate_by_name": True,
    }


class Kit(BaseModel):
    name: str
    description: Optional[str] = None
    quantity_per_subject: Optional[int] = None


class TestSpec(BaseModel):
    name: str
    category: str
    required: bool = True
    visit_name: Optional[str] = None
    notes: Optional[str] = None


class Site(BaseModel):
    site_id: str
    name: str
    country: Optional[str] = None
    city: Optional[str] = None
    role: Optional[str] = None


class Cohort(BaseModel):
    cohort_id: str
    name: str
    description: Optional[str] = None
    inclusion_criteria: List[str] = Field(default_factory=list)
    exclusion_criteria: List[str] = Field(default_factory=list)


class Visit(BaseModel):
    visit_id: str
    name: str
    window_days: Optional[str] = None
    purpose: Optional[str] = None
    required_tests: List[str] = Field(default_factory=list)


class StudySetup(BaseModel):
    study_id: str
    title: str
    protocol_version: str
    sites: List[Site] = Field(default_factory=list)
    cohorts: List[Cohort] = Field(default_factory=list)
    visits: List[Visit] = Field(default_factory=list)
    tests: List[TestSpec] = Field(default_factory=list)
    kits: List[Kit] = Field(default_factory=list)

    model_config = {
        "title": "StudySetup",
        "extra": "forbid",
    }


ClinicalTrialSetup.model_rebuild()
