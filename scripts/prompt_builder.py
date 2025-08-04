
import json
import logging
import os

def build_prompts(texto_pdf: str, plantilla_path: str, instrucciones_path: str) -> tuple:
    """
    Construye el system_prompt y user_prompt para usar en la API de OpenAI.

    :param texto_pdf: Texto completo extraído del PDF
    :param plantilla_path: Ruta al archivo plantilla.json
    :param instrucciones_path: Ruta al archivo intrucciones.json
    :return: (system_prompt, user_prompt)
    """
    logging.info("Cargando plantilla e instrucciones para construir el prompt...")

    try:
        with open(plantilla_path, "r", encoding="utf-8") as f:
            plantilla = json.load(f)
        with open(instrucciones_path, "r", encoding="utf-8") as f:
            instrucciones = json.load(f)
    except Exception as e:
        logging.error(f"Error al cargar los archivos JSON: {e}")
        return "", ""

    # SYSTEM PROMPT
    system_prompt = (
        "Eres un experto en análisis legal y ayudas públicas. "
        "Tu función es transformar documentos administrativos complejos "
        "en fichas sociales claras y estructuradas en formato JSON. "
        "Debes seguir exactamente la plantilla proporcionada y aplicar fielmente las instrucciones dadas para cada campo."
    )

    # USER PROMPT
    user_prompt = f"""
A continuación te proporciono:

1. El texto completo de un documento oficial extraído de un boletín.
2. La plantilla JSON que debes rellenar.
3. Las instrucciones detalladas para redactar y validar cada campo.

TEXTO DEL DOCUMENTO:
[INICIO_TEXTO]
{texto_pdf}
[FIN_TEXTO]

PLANTILLA JSON:
```json
{json.dumps(plantilla, indent=2, ensure_ascii=False)}
```

INSTRUCCIONES:
```json
{json.dumps(instrucciones, indent=2, ensure_ascii=False)}
```

INDICACIONES IMPORTANTES:

- Rellena todos los campos de la plantilla, incluso si no hay información: usa cadenas vacías "" o listas vacías [] si corresponde.
- No añadas explicaciones ni comentarios fuera del objeto JSON.
- No utilices encabezados, notas, ni envoltorios adicionales.
- Para los campos 'portales', 'categoría' y 'tipo_ayuda', selecciona únicamente los valores pertinentes al contenido del documento. 
  No devuelvas la lista completa ni incluyas términos no mencionados o irrelevantes.
- Asegúrate de seguir la redacción clara, directa y ordenada que indican las instrucciones.

Devuélveme únicamente un objeto JSON bien formado, respetando exactamente la estructura y los requisitos anteriores.
"""

    return system_prompt.strip(), user_prompt.strip()
