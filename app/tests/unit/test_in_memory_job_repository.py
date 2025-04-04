# app/tests/unit/test_in_memory_job_repository.py

from app.data.repositories.in_memory_job_repository import InMemoryJobRepository
from app.core.domain.entities.job_entity import Job

def test_in_memory_job_repository():
    repo = InMemoryJobRepository()
    job = Job(job_id="123")
    repo.create_job(job)

    fetched_job = repo.get_job("123")
    assert fetched_job == job

    job.status = "done"
    repo.update_job(job)
    fetched_job2 = repo.get_job("123")
    assert fetched_job2.status == "done"
