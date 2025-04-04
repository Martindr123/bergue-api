# app/core/domain/entities/letter_entity.py

from pydantic import BaseModel

class StructuredLetter(BaseModel):
    nom_prenom_client: str
    nom_prenom_adresse_client: str
    nom_de_l_affaire: str
    intro_lettre: str
    contexte_et_obj: str
    matiere_de_mission: str
    liste_missions: str
    honoraires: str

    class Config:
        extra = "forbid"
