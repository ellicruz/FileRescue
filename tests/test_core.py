import io
import zipfile

import pymupdf
import pytest

from filerescue.core import build_zip, extract_pdf_text, safe_stem, simulated_classification


def pdf_bytes(text="Comprovante de matrícula da universidade"):
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((72, 72), text)
        return doc.tobytes()


def test_extract_pdf_text():
    assert "matr" in extract_pdf_text(pdf_bytes()).lower()


def test_wrong_file_type():
    with pytest.raises(ValueError):
        extract_pdf_text(b"not a pdf")


def test_safe_stem_blocks_path_traversal():
    assert safe_stem("../../Meu Documento Final.pdf") == "meu_documento_final"


def test_demo_is_explicitly_not_ai():
    result = simulated_classification("Pagamento recebido em banco", "comprovante.pdf")
    assert result.category == "Financeiro"
    assert "SEM" not in result.reason or "Não houve uso de IA" in result.reason
    assert result.needs_review is True


def test_zip_is_non_destructive_and_unique():
    original = pdf_bytes()
    entries = [
        {"category": "Acadêmico", "new_name": "../matricula.pdf", "include": True, "data": original},
        {"category": "Acadêmico", "new_name": "../matricula.pdf", "include": True, "data": original},
        {"category": "Outros", "new_name": "ignored", "include": False, "data": original},
    ]
    archive = build_zip(entries)
    with zipfile.ZipFile(io.BytesIO(archive)) as zf:
        assert zf.namelist() == ["Acadêmico/matricula.pdf", "Acadêmico/matricula_2.pdf"]
        assert zf.read("Acadêmico/matricula.pdf") == original
    assert original.startswith(b"%PDF-")
