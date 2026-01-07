from distiller.reference_parser import parse_references


def test_parse_references_smoke():
    text = "Smith (2020) Example title. https://doi.org/10.1234/abc.1"
    entries = parse_references(text)
    assert entries
    assert entries[0].citation_key == "Smith-2020"
