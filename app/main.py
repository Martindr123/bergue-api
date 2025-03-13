# backend/app/main.py
import os
import io
import json
import uuid
import pdfplumber
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from docx import Document
from docxtpl import DocxTemplate
from datetime import datetime
from babel.dates import format_date

from .components.format_asterisks import convert_asterisks_to_rich_text
from .components.claude_answer import generate_claude_answer
from .components.openai_classification import parser_lettre

# Pour la sécurité (optionnel)
#from .security import verify_token

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, remplacer par les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montons le build React si on est en production:
BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "app_bergue", "frontend", "build")

if not os.path.exists(BUILD_DIR):
    raise FileNotFoundError(
        f"Le dossier de build '{BUILD_DIR}' n'existe pas. "
        "Veuillez exécuter 'npm run build' dans le dossier frontend avant de lancer l'API."
    )

# Cela permet de servir le front via FastAPI en production



@app.get("/api/healthcheck")
def healthcheck():
    return {"status": "ok"}


@app.post("/api/generate-doc")
async def generate_document(
    request: Request,
    compte_rendu_file: UploadFile = File(),
    description_missions: str = Form(),
    montant_provision: str = Form(),
    
    #payload=Depends(verify_token),  # Exige un token valide pour accéder à cette route
):
    """
    Route qui génère un document Word à partir du compte-rendu et des autres champs.
    """
    print("Requête reçue avec les données suivantes:")
    print(f"missions: {description_missions}")
    print(f"provision: {montant_provision}")
    
    # 1) Lire le contenu brut du fichier
    file_bytes = await compte_rendu_file.read()
    filename = compte_rendu_file.filename
    extension = os.path.splitext(filename)[1].lower()

    # 2) Extraire le texte selon le type
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

    # 3) Appeler tes fonctions de génération
    #infos_json = generer_infos_dossier(compte_rendu_text)
    #missions_honoraires = generate_missions_honoraires(compte_rendu_text, description_missions)
    
    # 4) Convertir en RichText ce qui doit être en gras
    #bold_missions = convert_asterisks_to_rich_text(missions_honoraires.liste_missions)

    claude_answer=generate_claude_answer(compte_rendu_text, description_missions)
    parsed_answer=parser_lettre(claude_answer)
    
    

    today = datetime.today()
    date_formatee = format_date(today, format='d MMMM yyyy', locale='fr_FR')
    

    # 5) Contexte pour docxtpl
    context = {
        "nom_prenom_adresse_client": convert_asterisks_to_rich_text(parsed_answer.nom_prenom_adresse_client),     
        "date_envoi_lettre": date_formatee,
        "contexte_et_obj": convert_asterisks_to_rich_text(parsed_answer.contexte_et_obj),
        "intro_lettre": convert_asterisks_to_rich_text(parsed_answer.intro_lettre),
        "nom_de_l_affaire": convert_asterisks_to_rich_text(parsed_answer.nom_de_l_affaire),
        "matiere_de_mission": convert_asterisks_to_rich_text(parsed_answer.matiere_de_mission),
        "liste_missions": convert_asterisks_to_rich_text(parsed_answer.liste_missions),
        "honoraires": convert_asterisks_to_rich_text(parsed_answer.honoraires),
        "montant_provision": montant_provision
    }

    # 6) Charger le template docx et rendre
    template_path = os.path.join(os.path.dirname(__file__), "templates", "model01.docx")
    doc = DocxTemplate(template_path)
    doc.render(context)

    output_stream = io.BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)

    # Retour en streaming
    return StreamingResponse(
        output_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=lettre_mission_{uuid.uuid4()}.docx"}
    )

#app.mount("/", StaticFiles(directory=BUILD_DIR, html=True), name="frontend")



# Si tu veux une route fallback pour le frontend React:
# (Uniquement si on ne monte pas un StaticFiles)
# ou si on veut que toute route non-API renvoie index.html
# (Décommenter si besoin)
#
# from fastapi.responses import HTMLResponse
# @app.get("/{full_path:path}")
# def react_catcher(full_path: str):
#     index_path = os.path.join(BUILD_DIR, "index.html")
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     else:
#         raise HTTPException(status_code=404, detail="Not Found")
