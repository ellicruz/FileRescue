# 📁 FileRescue — Resgate seus arquivos da bagunça digital

**MVP de organizador de documentos PDF com IA e revisão humana.**

O usuário envia PDFs, o sistema extrai texto com PyMuPDF, utiliza um modelo de linguagem para sugerir categoria e novo nome, apresenta as sugestões para revisão e entrega um ZIP com **cópias organizadas**. Os documentos originais não são alterados.

> Este projeto inicial é uma base de estudo. A integração com a API está implementada, mas precisa de uma chave válida, acesso ao modelo e conexão à internet para ser testada ao vivo.

## 1. Requisitos

- Python 3.11 ou superior.
- Um terminal (Windows PowerShell ou terminal do VS Code).
- Para o **modo IA**, chave válida da API OpenAI e acesso à rede. A assinatura do ChatGPT **não equivale a créditos de API**.

## 2. Instalação no Windows (PowerShell)

Extraia o ZIP, abra a pasta `FileRescue_MVP` no VS Code e rode:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Se `py` não estiver disponível, tente `python` no lugar.

## 3. Instalação no macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O navegador deve abrir `http://localhost:8501`.

## 4. Primeiro teste SEM custos

1. Escolha **Demonstração por regras (sem IA)** na barra lateral.
2. Envie os 3 PDFs fictícios da pasta `exemplos/`.
3. Clique em **Analisar arquivos**.
4. Revise categorias e nomes na tabela (é possível editá-los).
5. Baixe o ZIP organizado.

**Importante:** esse modo usa palavras-chave; **não é inteligência artificial**. Serve somente para conferir a interface e o fluxo.

## 5. Ativar a IA de verdade

1. Acesse o painel de API do provedor e crie uma chave com faturamento apropriado, se necessário.
2. Copie `.env.example` para `.env` e preencha `OPENAI_API_KEY`, ou cole a chave no campo protegido da interface.
3. Selecione **Inteligência artificial (API)** na barra lateral.
4. Use, inicialmente, o modelo `gpt-5.4-mini` (altere no campo se necessário).
5. Envie PDFs **fictícios**, clique em analisar e revise as respostas.

O modo IA extrai o texto localmente e envia ao provedor **somente o texto extraído (até 6.500 caracteres por PDF) e o nome original**. O provedor pode cobrar por uso. Evite PDFs pessoais, médicos, bancários ou sigilosos.

## 6. Arquitetura

```text
PDF(s) -> PyMuPDF -> Texto -> (LLM OU simulação por regras)
                                 -> Classificação + nome + justificativa
                                 -> Edição/aprovação humana
                                 -> ZIP com cópias organizadas
```

## 7. Testes

```bash
python -m pip install pytest
python -m pytest -q
```

## 8. Limites atuais

- Aceita até 10 PDFs digitais por análise, cada um com no máximo 10 MB.
- PDFs escaneados (somente imagem) ainda não passam por OCR.
- Não há busca semântica, login, integração com pastas locais nem armazenamento persistente.
- A opinião do modelo **não é garantia de acerto** e deve ser revisada.
- A interface funciona no computador local, sem deploy público.
- O modelo e disponibilidade da API podem mudar: ajuste conforme acesso e preço.

## 9. Evoluções sugeridas

- OCR para PDFs escaneados.
- Salvar histórico de análises com consentimento, sem armazenar documentos sensíveis.
- Detecção de duplicados por hash SHA-256.
- Busca semântica por perguntas em linguagem natural.
- Métricas de qualidade (acertos, ambiguidades, tempo médio) e demonstração gravada.

## 10. Créditos e responsabilidade

Implementação inicial preparada como exemplo educacional. Projetos públicos similares foram consultados apenas como referências conceituais; não copie código de terceiros sem verificar a licença e incluir atribuições exigidas. Teste e entenda o fluxo antes de descrever o projeto em currículo ou entrevista.
