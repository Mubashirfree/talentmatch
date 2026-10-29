from recruiter_bot.matching import availability_score,experience_score,score_match

def test_perfect_match_scores_100():
    r=score_match(8,"Immediate",3,3,2,["a","b","c"],["x","y"])
    assert r["score"] == 100.0

def test_experience_is_capped_at_one():
    assert experience_score(10,2) == 1.0 #overqualified get no extra points
    assert experience_score(1,4) == 0.25 #underqualified is scaled down

def test_not_looking_scores_lower_than_immediate():
    base=dict(years=5,min_experience=3,required_count=2,
              culture_count=1,matched_skills=["a","b"],matched_culture=[])
    immediate=score_match(availability="Immediate",**base)["score"]
    not_looking=score_match(availability="Not looking",**base)["score"]
    assert immediate > not_looking

def test_unknown_availability_is_neutral():
    assert availability_score("Someday") == 0.5


def test_breakdown_adds_up_to_score():
    r=score_match(8,"2 weeks",3,3,2,["a"],["x"])
    assert abs(sum(r["breakdown"].values())-r["score"])<0.05

