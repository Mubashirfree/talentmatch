"""FastAPI app . 
Run:uvicorn recruiter_bot.main:app --reload
Interactive docs: http://127.0.0.1:8000/docs
"""

import sqlite3

from fastapi import Depends,FastAPI,HTTPException,Query

from recruiter_bot.db import get_connection
from recruiter_bot.matching import rank_candidates_for_job,rank_jobs_for_candidate
from recruiter_bot.repository import insert_candidate,insert_job
from recruiter_bot.schemas import (CandidateIn,CandidateMatchesOut,CandidateOut,
                                   CandidateSummary,JobIn,JobMatchesOut,JobOut,JobSummary)

app=FastAPI(
    title="Recruiter Bot",
    description="Ranks candidates for jobs and jobs for candidates.",
    version="1.0.0",
)

def get_db():
    """Dependency:give each request its own connection and always close it."""
    conn=get_connection()
    try:
        yield conn
    finally:
        conn.close()

#reading

@app.get("/candidates",response_model=list[CandidateSummary])
def list_candidates(conn=Depends(get_db)):
    rows=conn.execute("SELECT id,name,experience_years,availability"
                      "FROM candidates ORDER BY id").fetchall()
    return [dict(r) for r in rows]

@app.get("/jobs",response_model=list[JobSummary])
def list_jobs(conn=Depends(get_db)):
    rows=conn.execute("SELECT id,title,min_experience FROM jobs ORDER BY id").fetchall()
    return [dict(r) for r in rows]


#matching
@app.get("/jobs/{job_id}/matches",response_model=JobMatchesOut)
def job_matches(
    job_id:int,
    limit:int |None=Query(None,ge=1,le=100,description="Return only the top N"),
    min_score:float=Query(0,ge=0,le=100,description="Hide scores belows this"),
    available_only:bool=Query(False,description="Hide 'Not looking' candidates "),
    conn=Depends(get_db),
):
    result=rank_candidates_for_job(conn,job_id,limit,min_score,available_only)
    if result is None:
        raise HTTPException(status_code=404,detail=f"Job {job_id} not found")
    return result

@app.get("/candidates/{candidate_id}/matches",response_model=CandidateOut,status_code=201)
def create_candidate(payload:CandidateIn,conn=Depends(get_db)):
    try:
        with conn: #commit on success ,roll back on error
            new_id=insert_candidate(conn,payload.name,payload.experience_years,
                                    payload.availability,payload.skills,payload.traits,payload.quirk)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409,
                            detail=f"Candidate '{payload.name}' already exists")
    return CandidateOut(id=new_id,**payload.model_dump())

@app.post("/jobs",response_model=JobOut,status_code=201)
def create_job(payload:JobIn,conn=Depends(get_db)):
    try:
        with conn:
            new_id=insert_job(conn,payload.title,payload.min_experience,
                              payload.skills,payload.culture,payload.tagline)

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=404,detail=f"Job '{payload.title}' already exists ")
    return JobOut(id=new_id,**payload.model_dump())
