import fitz  # PyMuPDF
import logging
import os

import spacy

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrae el texto completo de un archivo PDF usando PyMuPDF.
    Devuelve el texto como string.
    """
    if not os.path.isfile(pdf_path):
        logging.error(f"El archivo no existe: {pdf_path}")
        return ""

    logging.info(f"Extrayendo texto desde: {pdf_path}")
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for i, page in enumerate(doc):
            page_text = page.get_text()
            text += page_text + "\n"
            logging.debug(f"Página {i+1} procesada ({len(page_text)} caracteres)")
        logging.info(f"Extracción completada. Total páginas: {len(doc)}")
        return text.strip()
    except Exception as e:
        logging.exception("Error durante la extracción del PDF")
        return ""


# Inicializar spaCy una única vez
_nlp = spacy.blank("es")
_nlp.add_pipe("sentencizer")


def chunk_text(texto: str, max_tokens: int = 500, overlap: int = 50) -> list:
    """Divide el texto en fragmentos utilizando tokenización de spaCy.

    Los fragmentos se crean en función del número de tokens para preservar la
    mayor cantidad posible de información relevante. Se permite un solapamiento
    configurable para mantener el contexto entre fragmentos.

    Args:
        texto: Texto completo extraído del documento.
        max_tokens: Número máximo de tokens por fragmento.
        overlap: Número de tokens de solapamiento entre fragmentos.

    Returns:
        Lista de fragmentos de texto.
    """
    doc = _nlp(texto)
    tokens = [token.text for token in doc]

    chunks = []
    start = 0
    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunks.append(" ".join(chunk_tokens).strip())
        start = end - overlap

    logging.info(f"✅ Texto dividido en {len(chunks)} chunks usando spaCy.")
    return chunks
