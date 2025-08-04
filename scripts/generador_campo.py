import logging
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

from .openai_retry import call_with_retry

load_dotenv()
client = OpenAI(max_retries=0)

# Cargar instrucciones globales (una sola vez)
def cargar_instrucciones(ruta: str = "entradas/intrucciones.json") -> dict:
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"No se pudieron cargar las instrucciones: {e}")
        return {}

# Cargar lista cerrada de tipos de ayuda
def cargar_tipos_ayuda(ruta: str = "entradas/tipos_ayuda.json") -> List[str]:
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("tipos_de_ayuda", [])
    except Exception as e:
        logging.error(f"No se pudieron cargar los tipos de ayuda: {e}")
        return []

# Buscar instrucciones para un campo
def buscar_instrucciones_para_campo(campo: str, instrucciones_dict: dict) -> str:
    campo_normalizado = campo.lower().replace("_", " ")
    for clave, reglas in instrucciones_dict.items():
        if campo_normalizado in clave.lower():
            return "\n".join(f"- {linea}" for linea in reglas)
    return "(no se han definido instrucciones específicas)"

# Generar campo
def generar_campo_ficha(campo: str, chunks: List[str], instrucciones_dict: dict, tipos_ayuda: List[str] = None) -> str:
    """
    Genera el valor de un campo del JSON legal usando GPT-4o + instrucciones específicas.
    """
    try:
        texto_base = "\n\n".join(chunks)
        instrucciones_campo = buscar_instrucciones_para_campo(campo, instrucciones_dict)

        lista_restringida = ""
        if campo == "tipo_ayuda" and tipos_ayuda:
            lista_restringida = (
                "\n\nIMPORTANTE: debes seleccionar uno o varios términos exactamente iguales a los siguientes. "
                "No los modifiques ni inventes nada. Esta es una lista cerrada:\n"
                + ", ".join(tipos_ayuda)
            )

        user_prompt = f"""
Eres un asistente legal encargado de rellenar un único campo de una ficha técnica de ayudas públicas, siguiendo la normativa oficial y las instrucciones del proyecto Fichas Miguel.

Tu tarea es rellenar el campo **{campo}** de forma literal, clara y precisa, exclusivamente en base al contenido del documento original.

### INSTRUCCIONES PARA ESTE CAMPO
Sigue todas estas reglas literalmente. No ignores ninguna. No inventes.

{instrucciones_campo}
{lista_restringida}

### FRAGMENTOS RELEVANTES DE LA NORMA
Usa exclusivamente los siguientes fragmentos para construir tu respuesta. Si no hay datos suficientes, devuelve exactamente: ""

[INICIO_TEXTO]
{texto_base}
[FIN_TEXTO]

### REGLAS FINALES
- Devuelve solo el contenido final del campo "{campo}".
- No incluyas encabezados, comentarios ni explicaciones.
- No utilices bloques markdown como ```json.
- Si no hay suficiente información en los fragmentos, devuelve exactamente: ""
"""

        respuesta = call_with_retry(
            client.chat.completions.create,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Especialista en redacción legal estructurada para automatización de ayudas públicas. No debes inventar contenido bajo ningún concepto."},
                {"role": "user", "content": user_prompt.strip()}
            ],
            temperature=0.2,
        )

        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        logging.error(f"Error al generar el campo '{campo}': {e}")
        return ""
