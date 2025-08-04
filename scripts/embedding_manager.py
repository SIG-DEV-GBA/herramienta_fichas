import logging
import uuid
import chromadb
from openai import OpenAI
from typing import List
from dotenv import load_dotenv

from .openai_retry import call_with_retry

# Cargar API key desde .env
load_dotenv()

# Configuración
client = OpenAI(max_retries=0)
chroma_client = chromadb.Client()
CHROMA_COLLECTION = "documentos_legales"

def generar_embeddings(chunks: List[str], doc_id: str) -> None:
    """
    Genera embeddings para cada chunk y los guarda en una colección Chroma.
    """
    collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

    logging.info(f"Generando embeddings para {len(chunks)} chunks del documento: {doc_id}")
    
    for i, chunk in enumerate(chunks):
        try:
            resp = call_with_retry(
                client.embeddings.create,
                model="text-embedding-3-small",
                input=chunk,
            )
            embedding = resp.data[0].embedding

            chunk_id = f"{doc_id}_chunk_{i}"

            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[chunk_id],
                metadatas=[{"doc_id": doc_id, "chunk_index": i}]
            )

            logging.debug(f"Chunk {i} añadido con ID: {chunk_id}")

        except Exception as e:
            logging.error(f"Error generando embedding para chunk {i}: {e}")

    logging.info(f"Embeddings generados y guardados para el documento: {doc_id}")
