# app/data/repositories/in_memory_job_repository.py

from typing import Dict, Optional
from app.core.domain.entities.job_entity import Job
from app.core.domain.repositories.job_repository import JobRepository

class InMemoryJobRepository(JobRepository):
    def __init__(self):
        self._jobs: Dict[str, Job] = {}

    def create_job(self, job: Job) -> None:
        self._jobs[job.job_id] = job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update_job(self, job: Job) -> None:
        self._jobs[job.job_id] = job
