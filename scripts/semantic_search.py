"""Utilidades de búsqueda semántica en la base de datos de embeddings.

Este módulo se encarga de recuperar los fragmentos de texto más relevantes para un
campo concreto de la ficha. Durante el desarrollo se duplicó la inicialización de
la conexión con Chroma y se utilizaron dos nombres de colección distintos
(`documentos_legales` y `fichas_legales`). Como consecuencia, los embeddings se
almacenaban en una colección mientras las consultas se realizaban en otra, lo que
provocaba que no se recuperara ningún fragmento relevante.

Se ha unificado la configuración eliminando las inicializaciones duplicadas y
asegurando que tanto la generación como la consulta utilicen la misma colección
(`documentos_legales`).
"""

import logging
from typing import List

import chromadb
from openai import OpenAI
from dotenv import load_dotenv

from .openai_retry import call_with_retry

load_dotenv()

# Cliente de OpenAI para generar embeddings de las consultas
client = OpenAI()

# Cliente de Chroma para almacenar y consultar los embeddings
chroma_client = chromadb.Client()

# Nombre único de la colección utilizada en toda la aplicación
CHROMA_COLLECTION = "documentos_legales"

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
        embedding_resp = call_with_retry(
            client.embeddings.create,
            model="text-embedding-3-small",
            input=campo,
        )
        embedding = embedding_resp.data[0].embedding

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
