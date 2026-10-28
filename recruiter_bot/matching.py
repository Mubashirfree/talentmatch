"""
Matching algorithms:score how well a candidate fit in a job(0-100).

Score=weighted sum of four parts,each between 0 to 1:
                    calculated as
    skills      55%   matched required skills/total required skills
    experience  20%   years/min years capped at 1.0
    culture     10%   matched culture keywords/total culture keywords
    availability 20%  Immediate=1.0, 2 weeks=0.7, Not Looking=0.2

A candidate with Zero matching skills is excluded from the results entirely.
Every result also carries a  "breakdown":the points each part contributed,so
four numbers always add up to the total score.    

"""

WEIGHTS={"skills":0.55,"experience":0.20,"culture":0.10,"availability":0.15}
AVAILABILITY_SCORE={"Immediate":1.0,"2 weeks":0.7,"Not looking":0.2}


#------small pure functions(easy to unit test,no database)-------

def skill_score(matched:int,required:int)->float:
    """Fraction of the job's required skills the candidate has."""
    return matched/required if required else 0.0 

def experience_score(years:int,minimum:int)->float:
    """Candidate years vs the job minimum,capped at 1."""
    if minimum <=0:
        return 1.0
    return min(years/minimum,1.0)

def culture_score(matched:int,total:int)->float:
    """Fraction of the job's culture keywords the candidate's traits cover."""
    return matched/total if total else 0.0

def availability_score(availability:str)->float:
    """"Map the availability label to a number between 0.2 and 1."""
    return AVAILABILITY_SCORE.get(availability,0.5) #unknown value-> neutral    

def _split(csv_text):
    """GROUP_CONCAT gives 'a,b,c' or None; turn it into a list."""
    return csv_text.split(",") if csv_text else []

def score_match(years,availability,min_experience,required_count,culture_count,matched_skills,matched_culture)->dict:
    """Combine the four parts into a score,a breakdown and a reason."""
    parts={
        "skills":skill_score(len(matched_skills),required_count),
        "experience":experience_score(years,min_experience),
        "culture":culture_score(len(matched_culture),culture_count),
        "availability":availability_score(availability),
    }
    #points each part adds to the 0-100 score.Rounded once here, and the total
    #is the sum of the rounded points,so the breakdown always adds up exactly.

    breakdown={name:round(WEIGHTS[name]*value*100,1)
               for name,value in parts.items()}
    reason=(
        f"Matches {len(matched_skills)}/{required_count} required skills "
        f"({', '.join(matched_skills)}); {years} yrs vs {min_experience} required; "
        f"availability: {availability}"
    )
    if matched_culture:
        reason += f"; culture fit: {', '.join(matched_culture)}"
    return {"score":round(sum(breakdown.values()),1),
            "breakdown":breakdown,"reason":reason}

#------raw SQL:the database does the set-overlap work------

CANDIDATES_FOR_JOB_SQL="""
SELECT c.id,c.name,c.experience_years,c.availability,
    (SELECT GROUP_CONCAT(cs.skill)
        FROM  candidate_skills cs
         JOIN job_skills js ON  js.skill = cs.skill AND js.job_id = :job_id
         WHERE  cs.candidate_id =c.id) AS  matched_skills,
    (SELECT GROUP_CONCAT(ct.trait)
        FROM  candidate_traits ct
        JOIN job_culture jc ON jc.keyword=ct.trait AND  jc.job_id=:job_id
        WHERE ct.candidate_id=c.id) AS matched_culture
FROM candidates c
"""

JOBS_FOR_CANDIDATE_SQL="""
SELECT j.id,j.title,j.min_experience,
        (SELECT COUNT(*) FROM job_skills WHERE job_id=j.id) AS required_count,
        (SELECT COUNT(*) FROM job_culture WHERE job_id=j.id) AS culture_count,
        (SELECT GROUP_CONCAT(js.skill)
            FROM job_skills js
            JOIN candidate_skills cs ON cs.skill = js.skill AND cs.candidate_id=:cid
            WHERE  js.job_id=j.id) AS matched_skills,
        (SELECT GROUP_CONCAT(jc.keyword)
           FROM job_culture jc
            JOIN candidate_traits ct ON ct.trait=jc.keyword AND ct.candidate_id=:cid
           WHERE jc.job_id=j.id) AS matched_culture
FROM jobs j        
"""

def rank_candidates_for_job(conn,job_id,limit=None,min_score=0.0,
                            available_only=False):
    """
    limit :keep only the top N.min_score:drop scores below this.
    available_only:drop candidates whose availability is 'Not looking'. 
    """
    job=conn.execute(
        "SELECT id,title,min_experience,"
        "(SELECT COUNT(*) FROM job_skills WHERE job_id=jobs.id) AS required_count,"
       "(SELECT COUNT(*) FROM job_culture WHERE job_id=jobs.id) AS culture_count "
        "FROM jobs WHERE id = ?",
        (job_id,),
    ).fetchone()
    if job is None:
        return None
    results=[]
    for row in conn.execute(CANDIDATES_FOR_JOB_SQL,{"job_id":job_id}):
        matched_skills=_split(row["matched_skills"])
        if not matched_skills:
            continue #no skill overlap -> not a match
        if available_only and row["availability"] == "Not looking":
            continue
        scored=score_match(
            row["experience_years"],row["availability"],job["min_experience"],
            job["required_count"],job["culture_count"],
            matched_skills,_split(row["matched_culture"]),
        )
        if scored["score"]< min_score:
            continue
        results.append({"candidate_id":row["id"],"name":row["name"],"experience_years":row["experience_years"],**scored})
    #tie-break:higher score,then more experience,then name(stable out).
    results.sort(key=lambda r: (-r["score"],-r["experience_years"],r["name"]))
    return {"job":{"id":job["id"],"title":job["title"]},
            "matches":results[:limit]} #[:None] keeps everything

def rank_jobs_for_candidate(conn,candidate_id,limit=None,min_score=0.0):
    """Ranked jobs for one candidate,or None if the candidate doesn't exist."""
    cand=conn.execute(
        "SELECT id,name,experience_years,availability FROM  candidates WHERE id= ? ",
        (candidate_id,),
    ).fetchone()
    if cand is None:
        return None
    results=[]
    for row in conn.execute(JOBS_FOR_CANDIDATE_SQL,{"cid":candidate_id}):
        matched_skills=_split(row["matched_skills"])
        if not matched_skills:
            continue
        scored=score_match(
            cand["experience_years"],cand["availability"],row["min_experience"],
            row["required_count"],row["culture_count"],
            matched_skills,_split(row["matched_culture"]),
        )
        if scored["score"]< min_score:
            continue
        results.append({"job_id":row["id"],"title":row["title"],**scored})

    results.sort(key=lambda r:(-r["score"],r["title"]))
    return {"candidate":{"id":cand["id"],"name":cand["name"]},
            "matches":results[:limit]}

