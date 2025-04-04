# app/presentation/api/routes/doc_generation_router.py

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Form, HTTPException, Request
from app.data.repositories.in_memory_job_repository import InMemoryJobRepository

from app.core.use_cases.initiate_generation_use_case import initiate_generation_use_case
from app.core.use_cases.get_generation_status_use_case import get_generation_status_use_case
from app.core.use_cases.download_generated_doc_use_case import download_generated_doc_use_case

router = APIRouter()
job_repository = InMemoryJobRepository()  # dans un vrai code, on injecterait autrement

@router.post("/generate-doc/initiate")
async def initiate_generation(
    background_tasks: BackgroundTasks,
    compte_rendu_file: UploadFile = File(...),
    description_missions: str = Form(...),
    montant_provision: str = Form(...),
):
    result = initiate_generation_use_case(
        job_repository,
        background_tasks,
        compte_rendu_file,
        description_missions,
        montant_provision
    )
    return result

@router.get("/generate-doc/status")
def get_generation_status(job_id: str):
    return get_generation_status_use_case(job_repository, job_id)

@router.get("/generate-doc/download")
def download_generated_doc(job_id: str):
    return download_generated_doc_use_case(job_repository, job_id)
