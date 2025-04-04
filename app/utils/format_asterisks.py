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
        if match.start() > last_end:
            rt.add(text[last_end:match.start()], bold=False)
        rt.add(match.group(1), bold=True)
        last_end = match.end()

    if last_end < len(text):
        rt.add(text[last_end:], bold=False)

    return rt
