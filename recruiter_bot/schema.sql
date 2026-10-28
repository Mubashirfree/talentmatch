--recruiter Bot schema

--Drop children tables first so this file can be re-run safely.

DROP TABLE IF EXISTS candidate_skills;
DROP TABLE IF EXISTS candidate_traits;
DROP TABLE IF EXISTS job_skills;
DROP TABLE IF EXISTS job_culture;
DROP TABLE IF EXISTS candidates;
DROP TABLE IF EXISTS jobs;

CREATE TABLE candidates(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    experience_years INTEGER NOT NULL CHECK(
        experience_years >= 0
    ),
    availability TEXT NOT NULL CHECK(
        availability IN('Immediate', '2 weeks', 'Not looking')),
        quirk TEXT
    );

CREATE TABLE jobs(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    min_experience INTEGER NOT NULL CHECK(
        min_experience >= 0
    ),tagline TEXT
);



CREATE TABLE candidate_skills(
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    PRIMARY KEY(candidate_id,skill)
);

CREATE TABLE candidate_traits(
    candidate_id INTEGER NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    trait TEXT NOT NULL,
    PRIMARY KEY(candidate_id,trait)
);

CREATE TABLE job_skills(
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    PRIMARY KEY(job_id,skill)
);

CREATE TABLE job_culture(
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    PRIMARY KEY(job_id,keyword)
);

--Reverse lookups (skill -> who has it) need their own indexes.

CREATE INDEX idx_candidate_skills_skill  ON  candidate_skills(skill);
CREATE INDEX idx_job_skills_skill ON job_skills(skill);
