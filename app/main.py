# backend/app/main.py

import os
import io
import uuid
import pdfplumber
import uvicorn

from datetime import datetime
from babel.dates import format_date

from docx import Document
from docxtpl import DocxTemplate
from fastapi import FastAPI, BackgroundTasks, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .components.format_asterisks import convert_asterisks_to_rich_text
from .components.claude_answer import generate_claude_answer
from .components.openai_classification import parser_lettre


# ----- STOCKAGE EN MEMOIRE : job_id => {"status": ..., "file_bytes": ...} -----
jobs = {}  # { job_id: { "status": "pending"/"done"/"error", "file_bytes": <bytes ou None> } }


app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, vous pouvez restreindre ici
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/healthcheck")
def healthcheck():
    return {"status": "ok"}


# --------------------------------------------------------------------
# 1) INITIER LE PROCESSUS DE GENERATION
# --------------------------------------------------------------------
@app.post("/api/generate-doc/initiate")
async def initiate_generation(
    background_tasks: BackgroundTasks,
    compte_rendu_file: UploadFile = File(...),
    description_missions: str = Form(...),
    montant_provision: str = Form(...),
):
    """
    Lance la génération du document en tâche de fond.
    Retourne immédiatement un job_id pour que le frontend puisse suivre l'avancement.
    """
    # Créer un ID unique pour ce job
    job_id = str(uuid.uuid4())

    # Lire le fichier en mémoire tout de suite
    file_bytes = await compte_rendu_file.read()
    extension = os.path.splitext(compte_rendu_file.filename)[1].lower()

    # Stocker l'état initial du job
    # On ne stocke pas encore le "résultat" (file_bytes docx) car il n'est pas encore généré.
    jobs[job_id] = {
        "status": "pending",
        "file_bytes": None,
        "error": None,
    }

    # Planifier la tâche de génération en arrière-plan
    background_tasks.add_task(
        generate_doc_in_background,
        job_id,
        file_bytes,
        extension,
        description_missions,
        montant_provision
    )

    # On renvoie directement le job_id
    return {"job_id": job_id, "status": "started"}


# --------------------------------------------------------------------
# 2) FONCTION DE GENERATION EN TACHE DE FOND
# --------------------------------------------------------------------
def generate_doc_in_background(job_id, file_bytes, extension, description_missions, montant_provision):
    """
    Cette fonction est exécutée en background, sans bloquer la requête principale.
    On la sépare pour plus de lisibilité.
    """
    try:
        # 1) Extraire le texte brut du compte-rendu selon le type de fichier
        if extension == ".txt":
            try:
                compte_rendu_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                compte_rendu_text = "Impossible de décoder ce fichier .txt en UTF-8."
        elif extension == ".docx":
            docx_doc = Document(io.BytesIO(file_bytes))
            compte_rendu_text = "\n".join([p.text for p in docx_doc.paragraphs])
        elif extension == ".pdf":
            pdf_text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pdf_text += page_text + "\n"
            compte_rendu_text = pdf_text.strip()
        else:
            compte_rendu_text = f"Type de fichier non géré : {extension}"

        # 2) Appeler les fonctions de génération (Claude + OpenAI).
        claude_answer = generate_claude_answer(compte_rendu_text, description_missions)
        parsed_answer = parser_lettre(claude_answer)

        # 3) Préparer le contexte pour docxtpl
        today = datetime.today()
        date_formatee = format_date(today, format='d MMMM yyyy', locale='fr_FR')

        context = {
            "nom_prenom_client" : convert_asterisks_to_rich_text(parsed_answer.nom_prenom_client),
            "nom_prenom_adresse_client": convert_asterisks_to_rich_text(parsed_answer.nom_prenom_adresse_client),
            "date_envoi_lettre": date_formatee,
            "contexte_et_obj": convert_asterisks_to_rich_text(parsed_answer.contexte_et_obj),
            "intro_lettre": convert_asterisks_to_rich_text(parsed_answer.intro_lettre),
            "nom_de_l_affaire": convert_asterisks_to_rich_text(parsed_answer.nom_de_l_affaire),
            "matiere_de_mission": convert_asterisks_to_rich_text(parsed_answer.matiere_de_mission),
            "liste_missions": convert_asterisks_to_rich_text(parsed_answer.liste_missions),
            "honoraires": convert_asterisks_to_rich_text(parsed_answer.honoraires),
            "montant_provision": montant_provision,
        }

        # 4) Charger le template et générer le document
        template_path = os.path.join(os.path.dirname(__file__), "templates", "model01.docx")
        doc = DocxTemplate(template_path)
        doc.render(context)

        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        # 5) Mettre à jour le job : on stocke le docx final en bytes + status "done"
        jobs[job_id]["file_bytes"] = output_stream.read()
        jobs[job_id]["status"] = "done"

    except Exception as e:
        # S'il y a la moindre erreur, on stocke le message d'erreur
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


# --------------------------------------------------------------------
# 3) VERIFIER LE STATUT
# --------------------------------------------------------------------
@app.get("/api/generate-doc/status")
def get_generation_status(job_id: str):
    """
    Vérifie si le job est 'pending', 'done' ou 'error'.
    """
    job_info = jobs.get(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job non trouvé.")
    return {"status": job_info["status"], "error": job_info["error"]}


# --------------------------------------------------------------------
# 4) TELECHARGER LE DOCUMENT (SI DONE)
# --------------------------------------------------------------------
@app.get("/api/generate-doc/download")
def download_generated_doc(job_id: str):
    """
    Télécharge le fichier docx si le job est terminé.
    """
    job_info = jobs.get(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Job non trouvé.")
    if job_info["status"] != "done":
        raise HTTPException(status_code=400, detail="Le document n'est pas encore prêt.")

    file_bytes = job_info["file_bytes"]
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Aucun fichier généré.")

    filename = f"lettre_mission_{job_id}.docx"
    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    # Pour tester en local
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
