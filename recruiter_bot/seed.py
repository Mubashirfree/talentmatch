"""Create the tables and load the candidates and jobs.

Run from the project root : python -m recruiter_bot.seed
Safe to re-run:schema.sql drops and recreates every table.
"""

from recruiter_bot.db import SCHEMA_PATH, get_connection
from recruiter_bot.repository import insert_candidate,insert_job
from recruiter_bot.seed_data import CANDIDATES,JOBS

def seed()->None:
    conn=get_connection()
    #executescript  commits any open transaction first ,so run it on its own.
    conn.executescript(SCHEMA_PATH.read_text())
    with conn:
        for c in CANDIDATES:
            insert_candidate(conn,c["name"],c["years"],c["availability"],c["skills"],
                             c["traits"],c["quirk"])
        for j in JOBS:
            insert_job(conn,j["title"],j["min_exp"],j["skills"],j["culture"],j["tagline"])
    conn.close()
    print(f"Seeded {len(CANDIDATES)} candidates and {len(JOBS)} jobs.")

if __name__=="__main__":
    seed()
