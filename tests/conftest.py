"""
Shared test setup.Every test gets a brand-new seeded database in a temp
folder , so tests never touch  recruiter_bot.db and never affect each other.
"""

import pytest
from fastapi.testclient import TestClient

from recruiter_bot.main import app
from recruiter_bot.seed import seed

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv("RECRUITER_BOT_DB",str(tmp_path/"test.db"))
    seed()
    return TestClient(app)


