# app/tests/unit/test_format_asterisks.py

from api.utils.format_asterisks import convert_asterisks_to_rich_text

def test_convert_asterisks_to_rich_text():
    text = "Ceci est **important** et ceci est **super**."
    rt = convert_asterisks_to_rich_text(text)

    # Option 1 : checker via r_list
    # rt.r_list est une liste d'objets RichTextRun
    xml_str = rt.xml
    # Vérifier que les '**' ne figurent pas dans le XML
    assert '**' not in xml_str

    # Vérifier que le mot "important" apparaît dans le XML
    assert 'important' in xml_str
    # et que docxtpl ajoute bien la balise bold (par ex. <w:b/>) pour le rendre en gras
    assert '<w:b/>' in xml_str

