import os
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import json

current_dir = os.path.dirname(__file__)     # => app/components
config_path = os.path.join(current_dir, "..", "config", "config.json")  # => app/config.json
config_path = os.path.abspath(config_path)

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
    
openai_model=config.get("openai_model")

# Chargement des variables d'environnement (si tu utilises un fichier .env)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")





# Initialisation du client OpenAI
client = OpenAI(api_key=api_key)

# 1) Modèle Pydantic pour ta lettre structurée
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



def parser_lettre(claude_response: str):
    
    prompt_system="""

    Ton rôle est de parser la lettre de mission d'un avocat pour en extraire un JSON structuré, SANS AUCUN TEXTE SUPERFLU, dans le format suivant :
    {\"nom_prenom_client\": \"...\", (Exemple : **Madame Anne Martin** et **Monsieur Yves Dupont**)
    \"nom_prenom_adresse_client\": \"...\",  (Exemple : **Monsieur Yves Dupont**\n4 avenue du chemin de fer,\n78100 saint Germain en Laye\)
    \"nom_de_l_affaire\": \"...\", (le nom de l'affaire)
    \"intro_lettre\": \"...\", (la breve introduction en début de lettre)
    \"contexte_et_obj\": \"...\", (le paragraphe sous "Contexte et Objectifs de la Mission"
    \"matiere_de_mission\": \"...\", (Ex : droit de la copropriété, droit de la famille)
    \"liste_missions\": \"...\", (Le paragraphe sous "Descriptif de nos missions", jusqu'à la matière de mission, comprise)
    \"honoraires\": \"...\"}. (Le paragraphe sous "Honoraires")

     Lorsqu’un passage important apparaît dans la lettre (noms, dates, montants, etc.), entoure-le de doubles astérisques pour le mettre en gras. 
   - Par exemple, si la lettre mentionne : “Monsieur Yves Dupont”, tu l’écriras dans la clé correspondante comme : “**Monsieur Yves Dupont**”.
   - Si la lettre mentionne : “700 euros”, tu l’écriras : “**700 euros**”
   - N'oublie pas de mettre les balises backslash "t" lors des listes à puces pour tabuler.
   
    Retourne STRICTEMENT ce JSON. Tu n'inventeras rien, tu récupères seulement le texte dans cette  lettre :  

    """

    user_prompt=f"""
    Voici la lettre de mission à Parser :
    {claude_response}
    
    """

    messages_sequence = [
        {"role": "system", "content": prompt_system},
        {"role": "user", "content": user_prompt}]
    
    
    completion = client.beta.chat.completions.parse(
        model=openai_model,
        messages=messages_sequence,
        response_format=StructuredLetter,
        temperature=0.5
    )

    # Récupération du message et vérification d’un éventuel refus
    msg = completion.choices[0].message
    if msg.refusal:
        raise ValueError("Le modèle a refusé de répondre : " + msg.refusal)

    # L'attribut 'parsed' contient déjà un objet MissionsHonoraires
    response = msg.parsed

    return response




if __name__ == "__main__":
    claude_response="""
    
    Cabinet Valentin BERGUE\nAvocat au Barreau de Bayonne\n10 avenue de la Marne\n64200 BIARRITZ\nTél. : 05.59.22.33.44\ncontact@cabinet-bergue.fr\n\nMadame Karen ROUMIGUIER\n515 Allées d'Aouce\nRésidence L'Orée du Bois, Villa 9\n40230 BENESSE MAREMNE\n\nMonsieur Alexandre DENIS\n167 Chemin des Bambous\n40440 ONDRES\n\nA Biarritz,\nLe 22 février 2025,\n\n**Confidentiel**\n**Par mail**\nAffaire : Contestation des saisies-attributions pratiquées par Maître Julie DELOS\n\n# LETTRE DE MISSION\n\nChère Madame, Cher Monsieur,\n\nPour donner suite à notre rendez-vous du 21 février 2025 dernier à mon cabinet, je vous confirme les termes de notre collaboration concernant les saisies-attributions pratiquées sur vos comptes bancaires le 20 février 2025 par Maître Julie DELOS, Commissaire de Justice à Pouillon.\n\n## I. CONTEXTE ET OBJECTIF DE LA MISSION\n\nVous avez fait l'objet de saisies-attributions pratiquées sur vos comptes bancaires tenus par le C.I.C. SUD-OUEST, agence de Capbreton, à la demande des époux CASTAINGS (Thibaut et Marina), en vertu d'un jugement rendu par le Tribunal Judiciaire de DAX le 13 novembre 2024.\n\nCes saisies-attributions, notifiées le 20 février 2025, portent sur un montant total de 55.118,43 € pour chacun d'entre vous et concernent :\n- Pour Madame ROUMIGUIER : un montant saisissable de 73.088,26 €\n- Pour Monsieur DENIS : un montant saisissable de 26.609,50 €\n\nVous contestez ces saisies-attributions et souhaitez exercer les voies de recours légales dans le délai d'un mois à compter de la notification.\n\nNotre mission consistera à vous accompagner dans la contestation de ces mesures d'exécution forcée afin de préserver vos intérêts patrimoniaux.\n\n## II. DESCRIPTION DE NOS MISSIONS\n\nNotre rôle consistera dans les interventions suivantes :\n\n**MISSION 1 - Contestation de la saisie-attribution de Madame Karen ROUMIGUIER**\n1. Analyse approfondie des documents de saisie-attribution et du titre exécutoire\n2. Identification des moyens de contestation recevables (fond et forme)\n3. Rédaction et dépôt d'une assignation en contestation de saisie-attribution devant le Juge de l'Exécution du Tribunal Judiciaire de Dax\n4. Préparation du dossier de plaidoirie\n5. Représentation et plaidoirie à l'audience\n6. Suivi de la procédure jusqu'à la décision\n\n**MISSION 2 - Contestation de la saisie-attribution de Monsieur Alexandre DENIS**\n1. Analyse approfondie des documents de saisie-attribution et du titre exécutoire\n2. Identification des moyens de contestation recevables (fond et forme)\n3. Rédaction et dépôt d'une assignation en contestation de saisie-attribution devant le Juge de l'Exécution du Tribunal Judiciaire de Dax\n4. Préparation du dossier de plaidoirie\n5. Représentation et plaidoirie à l'audience\n6. Suivi de la procédure jusqu'à la décision\n\nNotre mission s'effectuera dans la matière suivante :\n- Droit de l'exécution\n- Procédure civile\n\n## III. EQUIPE ET CHAMP DE LA MISSION\n\nLes travaux seront sous la direction de Maître Valentin BERGUE avec qui vous entretenez des relations habituelles.\n\nNotre intervention se déroulera dans les limites fixées par la déontologie de notre profession, pour les besoins de la présente mission.\n\n## IV. HONORAIRES\n\nPour la mission décrite ci-dessus, nous évaluons nos honoraires forfaitairement en fonction du temps que nous estimons devoir consacrer à l'exécution des missions, hors des frais et dépenses que nous serions amenés à engager pour votre compte ou qui sont prévus par la présente.\n\nLes autres frais, débours et dépens seront réglés sans délai par le client, soit directement au professionnel qui les aura facturés, soit au cabinet qui en aura fait l'avance pour le compte du client.\n\nCes frais, débours et dépens comprennent notamment, sans que cette énumération soit exhaustive : frais d'huissier, de greffe, etc...\n\nLes frais de dossier seront forfaitisés sur la base de 10 % du montant HT des honoraires. Les frais d'envoi de recommandé sont forfaitisés à 18 €HT par envoi.\n\nLes frais de déplacement en voiture, hors ceux conventionnellement prévus, seront facturés sur la base de 0,50 € HT par kilomètre.\n\nNos honoraires pour les missions décrites ci-dessus seront les suivants :\n• MISSION 1 : 1.500 euros HT\n• MISSION 2 : 1.500 euros HT\n\nConformément aux usages de la profession, nous procèderons à la facturation de provisions à valoir sur les honoraires au fur et à mesure de l'avancement de la mission.\n\nLe budget proposé ci-dessus se fonde sur une estimation raisonnable du temps que nous consacrerons à la réalisation de cette mission.\n\nToute autre tâche que celles ci-dessus mentionnées au II pourra faire l'objet d'un devis spécifique ou sera facturée en plus sur la base du temps passé selon notre taux horaire 2025, à savoir :\n- RDV au Cabinet : 200 € HT\n- RDV extérieur : 300 € HT\n- Rédaction, autres tâches : 150 € HT\n\nJe vous prie d'agréer, Chère Madame, Cher Monsieur, l'expression de mes salutations distinguées.\n\nMaître Valentin BERGUE\nAvocat au Barreau de Bayonne"
    
    """
    print("test")
    parsed=parser_lettre(claude_response)
    print(parsed)