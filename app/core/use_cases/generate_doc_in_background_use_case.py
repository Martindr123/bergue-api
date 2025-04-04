# app/core/use_cases/generate_doc_in_background_use_case.py

import asyncio
from fastapi import UploadFile
from app.core.domain.repositories.job_repository import JobRepository
from app.core.domain.entities.job_entity import JobStatus
from app.core.domain.services.doc_generation_service import DocGenerationService

# On suppose que vous instanciez doc_generation_service quelque part (injection de dépendance).
# Ici, on admet qu’on l’importe comme variable globale ou qu’on le récupère autrement.
# En Clean Architecture, on injecte d’habitude via le "composition root".
# Pour l’exemple, on considère qu’on le récupère d’un conteneur ou variable globale.

from app.main import create_app  # si besoin, ou une autre façon de récupérer l'instance

# Dans un vrai code, on aurait un container d'injections. Pour l’exemple :
from app.infrastructure.services.anthropic_service import anthropic_client
from app.infrastructure.services.openai_service import openai_service

doc_generation_service = DocGenerationService(anthropic_client, openai_service)

async def generate_doc_in_background(
    job_id: str,
    job_repository: JobRepository,
    compte_rendu_file: UploadFile,
    description_missions: str,
    montant_provision: str
):
    """
    Fonction exécutée en tâche de fond (async). 
    On lit le fichier, on lance la génération, on met à jour le job.
    """
    try:
        # Lecture du fichier
        file_bytes = await compte_rendu_file.read()
        extension = "." + compte_rendu_file.filename.split(".")[-1] if "." in compte_rendu_file.filename else ""

        # Récupération job
        job = job_repository.get_job(job_id)
        if not job:
            return  # ou lever une exception

        # Extraction du texte
        compte_rendu_text = doc_generation_service.extract_text_from_file(file_bytes, extension)
        
        # Génération de la lettre structurée
        structured_letter = doc_generation_service.generate_letter(compte_rendu_text, description_missions)

        # Génération du .docx final
        file_result = doc_generation_service.build_docx_from_letter(structured_letter, montant_provision)

        # Mise à jour du job
        job.file_bytes = file_result
        job.status = JobStatus.DONE
        job_repository.update_job(job)

    except Exception as e:
        # Mise à jour du job en cas d’erreur
        job = job_repository.get_job(job_id)
        if job:
            job.status = JobStatus.ERROR
            job.error = str(e)
            job_repository.update_job(job)
