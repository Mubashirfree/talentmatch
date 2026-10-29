"""ALL Insert Statements lives here.so the seed
script and the API share them.
These functions do not commit.The caller wraps them in 'with conn:' so that
a candidate and all of their skills are saved together or not at all.
"""


def insert_candidate(conn,name,experience_years,availability,skills,traits,quirk=None):
    """Insert one candidate plus their skills and traits.Returns the new id."""
    cur=conn.execute(
        "INSERT INTO candidates(name,experience_years,availability,quirk)"
        "VALUES(?,?,?,?)",
        (name,experience_years,availability,quirk),

    )
    cid=cur.lastrowid
    conn.executemany(
        "INSERT INTO candidate_skills(candidate_id,skill) VALUES(?,?)",
        [(cid,s) for s in skills],
    )
    conn.executemany(
        "INSERT INTO candidate_traits(candidate_id,trait) VALUES(?,?)",
        [(cid,t) for t in traits]
    )
    return cid

def insert_job(conn,title,min_experience,skills,culture,tagline=None):
    """Insert one job plus its required skills and culture keywords.Returns the new id."""
    cur=conn.execute(
        "INSERT INTO jobs(title,min_experience,tagline) VALUES(?,?,?)", 
        (title,min_experience,tagline),
    )
    jid=cur.lastrowid
    conn.executemany(
        "INSERT INTO job_skills(job_id,skill) VALUES(?,?)",
        [(jid,s) for s in skills],
    )
    conn.executemany(
        "INSERT INTO job_culture(job_id,keyword) VALUES(?,?)",
        [(jid,k) for k in culture],
    )
    return jid