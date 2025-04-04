# app/core/use_cases/get_generation_status_use_case.py

from fastapi import HTTPException
from api.core.domain.repositories.job_repository import JobRepository

def get_generation_status_use_case(job_repository: JobRepository, job_id: str):
    job = job_repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé.")
    return {"status": job.status, "error": job.error}
