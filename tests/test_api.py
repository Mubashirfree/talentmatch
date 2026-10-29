"""
Integration tests:real HTTP  calls to the API against a temporary database.
"""

def test_job_matches_are_ranked_with_breakdown(client):
    res = client.get("/jobs/1/matches")
    assert res.status_code == 200
    top = res.json()["matches"][0]
    assert top["name"] == "Sherlock H."
    assert top["score"] == 95.0
    assert top["breakdown"] == {"skills": 55.0, "experience": 20.0,
                                "culture": 5.0, "availability": 15.0}


def test_limit_returns_only_top_n(client):
    res = client.get("/jobs/6/matches?limit=2")
    assert len(res.json()["matches"]) == 2


def test_min_score_filters_low_scores(client):
    names = [m["name"] for m in client.get("/jobs/1/matches?min_score=90").json()["matches"]]
    assert names == ["Sherlock H."]


def test_available_only_hides_not_looking(client):
    everyone = [m["name"] for m in client.get("/jobs/6/matches").json()["matches"]]
    available = [m["name"] for m in
                 client.get("/jobs/6/matches?available_only=true").json()["matches"]]
    assert "Michael S." in everyone
    assert "Michael S." not in available


def test_candidate_matches_reverse_direction(client):
    res = client.get("/candidates/6/matches")  # Rick S.
    assert res.status_code == 200
    assert res.json()["matches"][0]["title"] == "Rapid Prototyping Engineer"


def test_unknown_ids_return_404(client):
    assert client.get("/jobs/999/matches").status_code == 404
    assert client.get("/candidates/999/matches").status_code == 404


def test_bad_query_values_return_422(client):
    assert client.get("/jobs/1/matches?limit=0").status_code == 422
    assert client.get("/jobs/1/matches?min_score=101").status_code == 422


def test_create_candidate_then_find_in_matches(client):
    body = {"name": "Nancy D.", "experience_years": 6, "availability": "Immediate",
            "skills": ["Deduction", "Forensics"], "traits": ["analytical"]}
    res = client.post("/candidates", json=body)
    assert res.status_code == 201
    assert res.json()["id"] > 15
    names = [m["name"] for m in client.get("/jobs/1/matches").json()["matches"]]
    assert "Nancy D." in names


def test_skills_are_normalised_on_input(client):
    body = {"name": "Test T.", "experience_years": 1, "availability": "Immediate",
            "skills": ["Public Speaking", " public speaking "]}
    res = client.post("/candidates", json=body)
    assert res.json()["skills"] == ["public-speaking"]  # cleaned and de-duplicated


def test_duplicate_candidate_returns_409(client):
    body = {"name": "Sherlock H.", "experience_years": 8, "availability": "Immediate",
            "skills": ["deduction"]}
    assert client.post("/candidates", json=body).status_code == 409


def test_invalid_candidate_returns_422(client):
    bad_availability = {"name": "X", "experience_years": 1, "availability": "Maybe",
                        "skills": ["a"]}
    negative_years = {"name": "Y", "experience_years": -3, "availability": "Immediate",
                      "skills": ["a"]}
    no_skills = {"name": "Z", "experience_years": 1, "availability": "Immediate",
                 "skills": []}
    for body in (bad_availability, negative_years, no_skills):
        assert client.post("/candidates", json=body).status_code == 422


def test_create_job_then_rank_candidates_for_it(client):
    body = {"title": "Forensic Analyst", "min_experience": 2,
            "skills": ["forensics", "chemistry"], "culture": ["analytical"]}
    res = client.post("/jobs", json=body)
    assert res.status_code == 201
    matches = client.get(f"/jobs/{res.json()['id']}/matches").json()["matches"]
    assert {m["name"] for m in matches} >= {"Sherlock H.", "Rick S."}