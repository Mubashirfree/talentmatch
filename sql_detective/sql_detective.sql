-- Part 2: SQL Detective Challenge (SQLite syntax)
-- Run: sqlite3 -header -column hiring.db < sql_detective.sql

-- Q1: All currently open job postings with the owning recruiter's name.
SELECT jp.id, jp.title, r.name AS recruiter_name
FROM job_postings jp
JOIN recruiters r ON jp.recruiter_id = r.id
WHERE jp.status = 'open'
ORDER BY jp.id;

-- Q2: For each job posting, how many applicants reached the Final stage.
-- LEFT JOIN with the stage filter inside ON keeps postings with zero finalists.
SELECT jp.id, jp.title, COUNT(DISTINCT i.applicant_id) AS final_stage_applicants
FROM job_postings jp
LEFT JOIN interviews i
       ON jp.id = i.job_posting_id AND i.stage = 'Final'
GROUP BY jp.id, jp.title
ORDER BY jp.id;

-- Q3: People who effectively applied to more than one job posting.
-- The data is messy: Ananya Rao appears twice with different email casing.
-- Group by LOWER(email) to treat them as one person. The applicants table has
-- no job column, so "applied to a posting" is inferred from interviews.
SELECT LOWER(a.email) AS normalized_email,
       MIN(a.full_name) AS full_name,
       COUNT(DISTINCT i.job_posting_id) AS distinct_jobs_applied
FROM applicants a
JOIN interviews i ON a.id = i.applicant_id
GROUP BY LOWER(a.email)
HAVING COUNT(DISTINCT i.job_posting_id) > 1
ORDER BY full_name;

-- Q4: Final-stage conversion rate per recruiter (passed / total Final interviews),
-- only for recruiters with at least 3 Final-stage interviews.
SELECT r.name AS recruiter_name,
       COUNT(i.id) AS final_interviews,
       SUM(CASE WHEN i.outcome = 'passed' THEN 1 ELSE 0 END) AS passed,
       ROUND(100.0 * SUM(CASE WHEN i.outcome = 'passed' THEN 1 ELSE 0 END)
             / COUNT(i.id), 1) AS conversion_pct
FROM recruiters r
JOIN job_postings jp ON r.id = jp.recruiter_id
JOIN interviews i ON jp.id = i.job_posting_id
WHERE i.stage = 'Final'
GROUP BY r.id, r.name
HAVING COUNT(i.id) >= 3
ORDER BY r.id;

-- Q5 (Bonus): Recruiter with the most placements (Final + passed) per department.
-- The window function ranks recruiters inside each department; rank 1 = most
-- placements, and tied recruiters share rank 1 so both are shown.
WITH RecruiterPlacements AS (
    SELECT jp.department,
           r.name AS recruiter_name,
           COUNT(i.id) AS total_placements,
           DENSE_RANK() OVER (
               PARTITION BY jp.department
               ORDER BY COUNT(i.id) DESC
           ) AS placement_rank
    FROM job_postings jp
    JOIN recruiters r ON jp.recruiter_id = r.id
    JOIN interviews i ON jp.id = i.job_posting_id
    WHERE i.stage = 'Final' AND i.outcome = 'passed'
    GROUP BY jp.department, r.id, r.name
)
SELECT department, recruiter_name, total_placements
FROM RecruiterPlacements
WHERE placement_rank = 1
ORDER BY department;