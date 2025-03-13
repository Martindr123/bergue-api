import re
from docxtpl import RichText, DocxTemplate

def convert_asterisks_to_rich_text(text: str) -> RichText:
    """
    Transforme le texte pour que tout passage entre **double astérisques**
    apparaisse en gras (RichText) dans docxtpl.
    """
    pattern = re.compile(r"\*\*(.*?)\*\*")
    rt = RichText()
    last_end = 0

    for match in pattern.finditer(text):
        # Ajouter le texte normal avant la portion en gras
        if match.start() > last_end:
            rt.add(text[last_end:match.start()], bold=False)

        # Ajouter la portion en gras
        rt.add(match.group(1), bold=True)

        last_end = match.end()

    # Ajouter ce qui reste après le dernier bloc en gras
    if last_end < len(text):
        rt.add(text[last_end:], bold=False)

    return rt

if __name__ == "__main__":
    # Exemple de test unitaire rapide
    # 1) Exemple de texte brut à transformer
    texte_test = (
        """Voici un texte normal. **Ceci doit être en gras**. \n
        Et encore du texte **à mettre en gras** dans la même phrase."""
    )
    # 2) Conversion en RichText
    texte_rich = convert_asterisks_to_rich_text(texte_test)

    # 3) Exemple d’utilisation dans un DocxTemplate
    #    On suppose que vous avez un template (ex.: "test_template.docx")
    #    dans lequel vous avez un champ {{ mon_texte }}.
    doc = DocxTemplate(r"app\templates\model01.docx")

    # 4) Construire le contexte pour le rendu
    #    Utiliser des variables fictives si besoin
    context = {
        "nom_prenom_client": "essai",
        "adresse_client": "essai",
        "date_envoi_lettre": "date_envoi_lettre",
        "contexte_et_obj": "infos_json.context_et_obj",
        "intro_lettre": "infos_json.intro_lettre",
        "nom_de_l_affaire": "infos_json.nom_de_l_affaire",
        "matiere_de_mission": "infos_json.matiere_de_mission",
        "liste_missions": "missions_honoraires.liste_missions",
        "honoraires": "missions_honoraires.honoraires",
        "montant_provision": texte_rich  # NOUVEAU
    }

    # 5) Rendu & sauvegarde
    doc.render(context)
    doc.save("test_output.docx")
    print("Document généré : test_output.docx")
