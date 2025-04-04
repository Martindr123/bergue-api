# app/core/domain/repositories/job_repository.py

from abc import ABC, abstractmethod
from typing import Optional
from ..entities.job_entity import Job

class JobRepository(ABC):
    @abstractmethod
    def create_job(self, job: Job) -> None:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Optional[Job]:
        pass

    @abstractmethod
    def update_job(self, job: Job) -> None:
        pass
