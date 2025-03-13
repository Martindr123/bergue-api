import os
import anthropic

from dotenv import load_dotenv
import json

current_dir = os.path.dirname(__file__)     # => app/components
config_path = os.path.join(current_dir, "..", "config", "config.json")  # => app/config.json
config_path = os.path.abspath(config_path)

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)
    
claude_model = config.get("claude_model")
load_dotenv()
api_key = os.getenv("CLAUDE_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

txt_template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "model.txt")

with open(txt_template_path, 'r', encoding='utf-8') as file:
    model = file.read()

def generate_claude_answer(compte_rendu: str, missions_intro: str):
    prompt_user=f"""
    A l'aide du compte-rendu de réunion avec le client :
    {compte_rendu}
--------------------------

    Rédige la lettre de mission pour les missions suivantes : 
    {missions_intro}
   
    """
    
    prompt_system=f"""
    Tu es l'assistant d'un avocat expérimenté. Ton but est de l'assister dans la rédaction de lettres de missions.
    Voici un exemple d'une de ses lettres de missions, tu essayeras de te rapprocher de ce style de rédaction le plus possible. Renvoie aussi les zones de tabulations en mettant les balises (backslash t)) :

    {model}


    
    """
    response = client.messages.create(
    model=claude_model,
    max_tokens=5000,
    temperature=0.7,
    system=prompt_system,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_user
                }
            ]
        }
    ]
)
    return response.content[0].text





if __name__ == "__main__":
    compte_rendu="""
    Analyse des documents de saisie-attribution bancaire
J'ai examiné les deux ensembles de documents juridiques concernant des saisies-attributions effectuées par Maître Julie DELOS, Commissaire de Justice à Pouillon, France.
Premier ensemble de documents - Alexandre DENIS
Informations clés :
•	Date de la saisie : 20 février 2025
•	Débiteur : Alexandre DENIS (né le 8 novembre 1994 à Bayonne)
•	Adresse : 167 Chemin des Bambous, 40440 ONDRES
•	Créanciers : Thibaut CASTAINGS (né le 4 août 1988) et Marina CASTAINGS née PECASTAINGS (née le 27 février 1991)
•	Adresse des créanciers : Chemin Pontalery, Résidence Concordia, Apt 5, LE ROBERT (97231)
•	Banque : C.I.C. SUD-OUEST, agence de Capbreton
•	Montant total dû : 55 118,43 €
Détail de la dette :
•	Principal : 45 000,00 €
•	Article 700 (frais de procédure) : 2 500,00 €
•	Intérêts échus (taux de 7,21%) : 6 177,71 €
•	Provision pour intérêts à échoir (1 mois) : 266,67 €
•	Frais d'exécution TTC : 720,61 €
•	Émolument proportionnel : 43,85 €
•	Frais de la présente procédure : 289,81 €
•	Coût de l'acte TTC : 119,78 €
Informations sur le compte bancaire :
•	Titulaire du compte : Alexandre DENIS et MME K ROUMIGUIER
•	Numéro de compte : 00020476203
•	Total disponible : 27 245,21 €
•	Montant protégé (RSA) : 635,71 €
•	Montant saisissable : 26 609,50 €
•	Total des fonds réservés : 73 491,02 €
Deuxième ensemble de documents - Karen ROUMIGUIER
Informations clés :
•	Date de la saisie : 20 février 2025
•	Débitrice : Karen Dominique Cynthia ROUMIGUIER (née le 10 juin 1996 à Bayonne)
•	Adresse : 3 Bis Allée de Bretagne, 40530 LABENNE (actuellement au : 515 Allées d'Aouce, Résidence L'Orée du Bois, Villa 9, 40230 BENESSE MAREMNE)
•	Créanciers : Identiques au premier cas (Thibaut et Marina CASTAINGS)
•	Banque : C.I.C. SUD-OUEST, agence de Capbreton
•	Montant total dû : 55 118,43 € (identique au premier cas)
Détail de la dette : Identique au cas précédent
Informations sur le compte bancaire :
•	Total disponible : 73 723,97 €
•	Montant protégé (RSA) : 635,71 €
•	Montant saisissable : 73 088,26 €
Procédure légale et délais
Les deux débiteurs ont été informés que :
1.	Ils disposent d'un mois pour contester la saisie à compter de la date de notification
2.	Ils peuvent autoriser le paiement immédiat pour arrêter le cours des intérêts
3.	Une somme de 635,71 € (équivalent au RSA) est protégée de la saisie
4.	Les contestations doivent être déposées auprès du Tribunal Judiciaire de Dax
La base juridique de cette saisie est un jugement rendu par le Tribunal Judiciaire de DAX le 13 novembre 2024, qui a été préalablement signifié à l'avocat le 25 novembre 2024.
Les deux dossiers comprennent un formulaire d'"Acquiescement à Saisie Attribution" qui permettrait aux débiteurs d'accepter formellement la saisie et d'autoriser la banque à transférer les fonds directement aux créanciers via le Commissaire de Justice.


    """
    
    missions_intro="""
    Mission 1 - Contestation de la saisie-attribution de Mme Karen ROUMIGER (1500€)
    Mission 2 (1500 euros) - Contestation de la saisie-attribution de M. Alexandre Denis
    """
    
    test=generate_claude_answer(compte_rendu, missions_intro)
    print(test)