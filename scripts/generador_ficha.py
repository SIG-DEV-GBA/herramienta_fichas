import json
import logging
from scripts.semantic_search import buscar_chunks_relevantes
from scripts.generador_campo import generar_campo_ficha, cargar_instrucciones, cargar_tipos_ayuda


def cargar_plantilla(path: str = "entradas/plantilla.json") -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar plantilla: {e}")
        return {}


def rellenar_ficha(doc_id: str, campos_objetivo: list = None) -> dict:
    """
    Genera un objeto JSON completo para una ficha legal.

    :param doc_id: ID único del documento procesado
    :param campos_objetivo: lista de campos a rellenar (por defecto todos los campos principales)
    :return: diccionario con la ficha completa
    """
    plantilla = cargar_plantilla()
    instrucciones = cargar_instrucciones("entradas/intrucciones.json")
    tipos_ayuda = cargar_tipos_ayuda("entradas/tipos_ayuda.json")

    if campos_objetivo is None:
        campos_objetivo = [
            "denominacion_normativa_nombre_ayuda",
            "portales",
            "categoria",
            "tipo_ayuda",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "fecha_publicacion",
            "ambito_territorial",
            "administracion",
            "plazo_presentacion",
            "requisitos_acceso",
            "destinatarios",
            "cuantia",
            "importe_maximo",
            "costes_no_subvencionables",
            "resolucion",
            "documentos_presentar",
            "publicacion_normativa",
            "normativa_reguladora",
            "referencia_legislativa",
            "usuario",
            "fecha",
            "organismo",
            "frase_publicitaria",
            "lugares_presentacion"
        ]

    ficha = plantilla.copy()

    for campo in campos_objetivo:
        logging.info(f"🟨 Generando campo: '{campo}' ...")
        try:
            chunks = buscar_chunks_relevantes(campo.replace("_", " "), doc_id=doc_id, top_n=20)
            contenido = generar_campo_ficha(campo, chunks, instrucciones, tipos_ayuda=tipos_ayuda)
            ficha[campo] = contenido
        except Exception as e:
            logging.error(f"❌ Error procesando campo '{campo}': {e}")
            ficha[campo] = ""

    return ficha


def guardar_ficha(ficha: dict, nombre_archivo: str = "ficha_resultado.json"):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=2)
    logging.info(f"Ficha guardada en {nombre_archivo}")
