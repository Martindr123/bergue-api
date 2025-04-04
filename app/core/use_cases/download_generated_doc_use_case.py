# app/core/use_cases/download_generated_doc_use_case.py

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import io
from app.core.domain.repositories.job_repository import JobRepository
from app.core.domain.entities.job_entity import JobStatus

def download_generated_doc_use_case(job_repository: JobRepository, job_id: str):
    job = job_repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job non trouvé.")
    if job.status != JobStatus.DONE:
        raise HTTPException(status_code=400, detail="Le document n'est pas encore prêt.")
    if not job.file_bytes:
        raise HTTPException(status_code=400, detail="Aucun fichier généré.")

    filename = f"lettre_mission_{job_id}.docx"
    return StreamingResponse(
        io.BytesIO(job.file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
