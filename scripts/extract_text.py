import fitz  # PyMuPDF
import logging
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

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


def chunk_text(texto: str, chunk_size: int = 1200, chunk_overlap: int = 300) -> list:
    """
    Divide el texto en chunks con solapamiento generoso para preservar contexto.
    Devuelve una lista de strings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
        add_start_index=True  # opcional para trazabilidad
    )
    chunks = splitter.split_text(texto)
    logging.info(f"✅ Texto dividido en {len(chunks)} chunks.")
    return chunks
