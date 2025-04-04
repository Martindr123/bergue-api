# app/core/domain/services/doc_generation_service.py

import io
import os
import pdfplumber
from docx import Document
from docxtpl import DocxTemplate
from datetime import datetime
from babel.dates import format_date

from app.utils.format_asterisks import convert_asterisks_to_rich_text
from app.infrastructure.services.anthropic_service import AnthropicClient
from app.infrastructure.services.openai_service import OpenAIService
from app.core.domain.entities.letter_entity import StructuredLetter

class DocGenerationService:

    def __init__(self, anthropic_client: AnthropicClient, openai_service: OpenAIService):
        self.anthropic_client = anthropic_client
        self.openai_service = openai_service

    def extract_text_from_file(self, file_bytes: bytes, extension: str) -> str:
        """
        Extrait le texte brut du fichier (txt, docx, pdf, etc.).
        """
        extension = extension.lower()
        if extension == ".txt":
            try:
                return file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return "Impossible de décoder ce fichier .txt en UTF-8."
        elif extension == ".docx":
            docx_doc = Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in docx_doc.paragraphs])
        elif extension == ".pdf":
            pdf_text = ""
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    pdf_text += page_text + "\n"
            return pdf_text.strip()
        else:
            return f"Type de fichier non géré : {extension}"

    def generate_letter(self, compte_rendu_text: str, description_missions: str) -> StructuredLetter:
        """
        1) Appelle Claude pour produire une lettre au style avocat
        2) Parse la réponse avec OpenAI pour obtenir un JSON structuré
        """
        claude_answer = self.anthropic_client.generate_claude_answer(
            compte_rendu=compte_rendu_text,
            missions_intro=description_missions
        )
        structured_letter = self.openai_service.parser_lettre(claude_answer)
        return structured_letter

    def build_docx_from_letter(self, structured_letter: StructuredLetter, montant_provision: str) -> bytes:
        """
        Rendu du docx final via docxtpl.
        """
        # Récupérer la date du jour
        today = datetime.today()
        date_formatee = format_date(today, format='d MMMM yyyy', locale='fr_FR')

        # Construire le contexte
        context = {
            "nom_prenom_client": convert_asterisks_to_rich_text(structured_letter.nom_prenom_client),
            "nom_prenom_adresse_client": convert_asterisks_to_rich_text(structured_letter.nom_prenom_adresse_client),
            "date_envoi_lettre": date_formatee,
            "contexte_et_obj": convert_asterisks_to_rich_text(structured_letter.contexte_et_obj),
            "intro_lettre": convert_asterisks_to_rich_text(structured_letter.intro_lettre),
            "nom_de_l_affaire": convert_asterisks_to_rich_text(structured_letter.nom_de_l_affaire),
            "matiere_de_mission": convert_asterisks_to_rich_text(structured_letter.matiere_de_mission),
            "liste_missions": convert_asterisks_to_rich_text(structured_letter.liste_missions),
            "honoraires": convert_asterisks_to_rich_text(structured_letter.honoraires),
            "montant_provision": montant_provision,
        }

        # Charger le template
        template_path = os.path.join(os.path.dirname(__file__), "..", "..", "..",
                                     "presentation", "templates", "model01.docx")
        template_path = os.path.abspath(template_path)
        doc = DocxTemplate(template_path)

        # Rendu
        doc.render(context)

        # Sauvegarde en mémoire
        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)

        return output_stream.read()
