# app/utils/format_asterisks.py

import re
from docxtpl import RichText

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

