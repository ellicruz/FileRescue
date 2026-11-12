"""Interface Streamlit para o MVP FileRescue."""
from __future__ import annotations

import hashlib
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from filerescue.core import (
    CATEGORIES,
    ai_classification,
    build_zip,
    extract_pdf_text,
    safe_stem,
    simulated_classification,
)

load_dotenv()
st.set_page_config(page_title="FileRescue | Organize PDFs com IA", page_icon="📁", layout="wide")

st.title("📁 FileRescue")
st.caption("Resgate seus arquivos da bagunça digital • MVP demonstrável")
st.write(
    "Envie PDFs, confira sugestões de categoria e nome e baixe uma **cópia organizada em ZIP**. "
    "Seus arquivos originais **nunca são alterados**."
)

with st.sidebar:
    st.header("Configuração")
    mode = st.radio(
        "Modo de análise",
        ["Demonstração por regras (sem IA)", "Inteligência artificial (API)"],
        help="O modo de demonstração não faz chamadas a modelos de IA.",
    )
    api_key = ""
    model = "gpt-5.4-mini"
    if mode == "Inteligência artificial (API)":
        api_key = st.text_input(
            "Chave da API OpenAI",
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password",
            help="Nunca compartilhe a chave em prints ou no GitHub.",
        )
        model = st.text_input("Modelo", value="gpt-5.4-mini")
        st.caption("O texto extraído dos PDFs é enviado ao provedor da API. Use apenas arquivos fictícios ou autorizados.")
    else:
        st.info("Modo de teste: classificação com palavras-chave, SEM inteligência artificial.")
    st.caption("A assinatura do ChatGPT não inclui automaticamente créditos da API.")

files = st.file_uploader(
    "Selecione até 10 arquivos PDF (máximo 10 MB por arquivo)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Para começar, use os PDFs fictícios da pasta exemplos/.",
)

if files and len(files) > 10:
    st.error("Envie no máximo 10 arquivos por vez.")

can_analyze = bool(files) and len(files) <= 10 and ("sem IA" in mode or bool(api_key.strip()))
if st.button("🔎 Analisar arquivos", type="primary", disabled=not can_analyze):
    st.session_state.pop("results", None)
    st.session_state.pop("sources", None)
    results = []
    sources = {}
    progress = st.progress(0)
    for idx, uploaded in enumerate(files):
        data = uploaded.getvalue()
        key = hashlib.sha256(data + str(idx).encode()).hexdigest()[:20]
        try:
            text = extract_pdf_text(data)
            if not text:
                st.warning(f"**{uploaded.name}:** PDF sem texto selecionável. OCR ainda não faz parte do MVP.")
                continue
            if mode == "Inteligência artificial (API)":
                classification = ai_classification(text, uploaded.name, api_key, model)
            else:
                classification = simulated_classification(text, uploaded.name)
            results.append(
                {
                    "Identificador": key,
                    "Arquivo original": uploaded.name,
                    "Categoria": classification.category,
                    "Novo nome": safe_stem(classification.proposed_name) + ".pdf",
                    "Justificativa": classification.reason,
                    "Revisão necessária": classification.needs_review,
                    "Incluir": True,
                }
            )
            sources[key] = data
        except Exception as exc:
            st.error(f"Não foi possível analisar **{uploaded.name}**: {exc}")
        progress.progress((idx + 1) / len(files))
    if results:
        st.session_state["results"] = results
        st.session_state["sources"] = sources
        st.success(f"{len(results)} documento(s) analisado(s). Revise as sugestões abaixo.")

if st.session_state.get("results"):
    st.subheader("Revise antes de organizar")
    if mode == "Demonstração por regras (sem IA)":
        st.warning("ATENÇÃO: estas sugestões foram geradas por regras fixas. Não são um resultado de IA.")
    table = pd.DataFrame(st.session_state["results"])
    edited = st.data_editor(
        table,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Identificador", "Arquivo original", "Justificativa", "Revisão necessária"],
        column_config={
            "Identificador": None,
            "Categoria": st.column_config.SelectboxColumn("Categoria", options=CATEGORIES, required=True),
            "Novo nome": st.column_config.TextColumn("Novo nome", help="Você pode corrigir o nome sugerido."),
            "Incluir": st.column_config.CheckboxColumn("Incluir no ZIP"),
        },
    )
    entries = []
    for _, row in edited.iterrows():
        source = st.session_state["sources"].get(row["Identificador"])
        if source is not None:
            entries.append(
                {
                    "category": row["Categoria"],
                    "new_name": row["Novo nome"],
                    "include": bool(row["Incluir"]),
                    "data": source,
                }
            )
    if any(entry["include"] for entry in entries):
        zip_bytes = build_zip(entries)
        st.download_button(
            "⬇️ Baixar arquivos organizados (ZIP)",
            data=zip_bytes,
            file_name="FileRescue_organizados.zip",
            mime="application/zip",
            type="primary",
        )
        st.caption("O ZIP contém apenas cópias. Nenhum documento original é renomeado, movido ou excluído.")
    else:
        st.info("Marque pelo menos um documento para gerar o ZIP.")

st.divider()
with st.expander("Limitações e privacidade", expanded=False):
    st.write(
        "Esta versão lê PDFs digitais com texto extraível. PDFs escaneados e imagens exigem OCR (versão futura). "
        "O conteúdo pode ser truncado para limitar custo e exposição de dados. "
        "No modo IA, apenas o texto extraído e o nome original são enviados ao provedor selecionado; "
        "não envie dados sensíveis, pessoais ou documentos confidenciais em testes. "
        "A classificação deve ser revisada por uma pessoa."
    )
