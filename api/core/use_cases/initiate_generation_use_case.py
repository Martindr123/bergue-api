# app/core/use_cases/initiate_generation_use_case.py

import uuid
from fastapi import BackgroundTasks, UploadFile, File, Form
from api.core.domain.entities.job_entity import Job, JobStatus
from api.core.domain.repositories.job_repository import JobRepository
from .generate_doc_in_background_use_case import generate_doc_in_background

def initiate_generation_use_case(
    job_repository: JobRepository,
    background_tasks: BackgroundTasks,
    compte_rendu_file: UploadFile = File(...),
    description_missions: str = Form(...),
    montant_provision: str = Form(...)
):
    """
    Lance la génération du document en tâche de fond.
    Retourne un job_id.
    """
    job_id = str(uuid.uuid4())
    job = Job(job_id=job_id, status=JobStatus.PENDING, file_bytes=None, error=None)
    job_repository.create_job(job)

    # On lit le fichier en mémoire ici car on en aura besoin dans le background
    # (sinon, on perd le file stream).
    file_bytes = background_tasks.add_task(
        generate_doc_in_background,
        job_id,
        job_repository,
        compte_rendu_file,
        description_missions,
        montant_provision
    )

    return {"job_id": job_id, "status": "started"}
 