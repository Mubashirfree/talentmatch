"""
Pydantic models:they validate incoming JSON  and describe outgoing JSON.

FastAPI reads these to (1)reject bad input with a 422 error automatically and
(2) build the interactive docs page at /docx.

"""
from typing import Literal

from pydantic import BaseModel,Field,field_validator

Availability=Literal["Immediate","2 weeks","Not looking"]

def clean_tags(values:list[str])->list[str]:
    """Normalise skills/traits:'Public Speaking'->'public-speaking',no duplicates."""
    cleaned=[]
    for v in values:
        tag="-".join(v.strip().lower().split())
        if tag and tag not in cleaned:
            cleaned.append(tag)
        return cleaned

#input (what client sends)

class CandidateIn(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    experience_years:int=Field(ge=0,le=60)
    availability:Availability
    skills:list[str]=Field(min_length=1)
    traits:list[str]=[]
    quirk:str | None=None

    @field_validator("skills","traits")
    @classmethod
    def normalise(cls,values):
        return clean_tags(values)

    @field_validator("skills")
    @classmethod
    def need_one_skill(cls,values):
        if not values:
            raise ValueError("at least one non-empty skill is required")
        return values

class JobIn(BaseModel):
    title:str=Field(min_length=1,max_length=100)
    min_experience:int=Field(ge=0,le=60)
    skills:list[str]=Field(min_length=1)
    culture:list[str]=[]
    tagline:str | None = None

    @field_validator("skills","culture")
    @classmethod
    def normalise(cls,values):
        return clean_tags(values)

    @field_validator("skills")
    @classmethod
    def need_one_skill(cls,values):
        if not values:
            raise ValueError("at least one non-empty skill is required")
        return values

#output (what the API returns)

class CandidateOut(CandidateIn):
    id:int

class JobOut(JobIn):
    id:int

class CandidateSummary(BaseModel):
    id:int
    name:str
    experience_years:int
    availability:str

class JobSummary(BaseModel):
    id:int
    title:str
    min_experience:int

class Breakdown(BaseModel):
    """Points each part contributed to the 0-100 score."""
    skills:float
    experience:float
    culture:float
    availability:float

class CandidateMatch(BaseModel):
    candidate_id:int
    name:str
    experience_years:int
    score:float
    breakdown:Breakdown
    reason:str


class JobMatch(BaseModel):
    job_id:int
    title:str
    score:float
    breakdown:Breakdown
    reason:str

class JobRef(BaseModel):
    id:int
    title:str

class CandidateRef(BaseModel):
    id:int
    name:str


class JobMatchesOut(BaseModel):
    job:JobRef
    matches:list[CandidateMatch]

class CandidateMatchesOut(BaseModel):
    candidate:CandidateIn
    matches:list[JobMatch]




    