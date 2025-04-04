# app/tests/unit/test_format_asterisks.py

from app.utils.format_asterisks import convert_asterisks_to_rich_text

def test_convert_asterisks_to_rich_text():
    text = "Ceci est **important** et ceci est **super**."
    rt = convert_asterisks_to_rich_text(text)

    # rt est un RichText, on peut vérifier son contenu en accédant à rt.xml ou via docxtpl
    # Pour un test simple :
    assert "**" not in rt.text  # On s'attend à ce que les ** soient enlevés
    # On peut tester un peu plus finement en examinant rt.r_list...
    assert "important" in rt.text
