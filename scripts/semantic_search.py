import logging
from openai import OpenAI
import chromadb
from typing import List
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
chroma_client = chromadb.Client()
CHROMA_COLLECTION = "documentos_legales"

from typing import List
import logging
from openai import OpenAI
from chromadb import Client  # o como tengas definido tu cliente Chroma

# Asegúrate de tener estas variables definidas en tu entorno
client = OpenAI()
chroma_client = Client()
CHROMA_COLLECTION = "fichas_legales"

def buscar_chunks_relevantes(campo: str, doc_id: str, top_n: int = 10) -> List[str]:
    """
    Busca los chunks más relevantes para un campo específico de un documento.

    :param campo: texto de la consulta, por ejemplo: 'requisitos de acceso'
    :param doc_id: ID del documento al que pertenecen los chunks
    :param top_n: número de chunks a recuperar (por defecto 10)
    :return: lista de textos relevantes
    """
    try:
        # Embedding de la consulta
        embedding = client.embeddings.create(
            model="text-embedding-3-small",
            input=campo
        ).data[0].embedding

        # Recuperar colección y buscar
        collection = chroma_client.get_or_create_collection(name=CHROMA_COLLECTION)

        resultados = collection.query(
            query_embeddings=[embedding],
            n_results=top_n,
            where={"doc_id": doc_id}
        )

        chunks = resultados["documents"][0]
        logging.info(f"🔍 Recuperados {len(chunks)} chunks relevantes para campo: {campo}")
        return chunks

    except Exception as e:
        logging.error(f"❌ Error en búsqueda semántica para '{campo}': {e}")
        return []
