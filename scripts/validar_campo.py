import re
import json
import logging
from typing import Union, Any

def limpiar_respuesta_cruda(respuesta: str) -> str:
    """
    Elimina decoraciones tipo markdown, comillas innecesarias o bloques ```json.
    """
    if not respuesta:
        return ""

    # Eliminar bloques tipo ```json ... ```
    respuesta = re.sub(r"^```json\s*|```$", "", respuesta.strip(), flags=re.IGNORECASE)

    # Eliminar comillas envolventes innecesarias
    if respuesta.startswith('"') and respuesta.endswith('"'):
        respuesta = respuesta[1:-1]

    # Quitar espacios extraños y saltos excesivos
    return respuesta.strip()

def parsear_a_objeto(valor: str) -> Union[str, list, dict]:
    """
    Intenta convertir una string en dict o list si parece JSON válido.
    Si falla, devuelve la string limpia.
    """
    try:
        return json.loads(valor)
    except json.JSONDecodeError:
        return valor.strip()

def validar_y_limpiar_campo(respuesta_cruda: str) -> Union[str, list, dict]:
    """
    Aplica limpieza + intento de parseo estructurado.
    """
    limpia = limpiar_respuesta_cruda(respuesta_cruda)
    resultado = parsear_a_objeto(limpia)

    if isinstance(resultado, (dict, list, str)):
        return resultado
    else:
        logging.warning("Formato no reconocido tras limpiar/parsing.")
        return limpia

def tipo_esperado_por_campo(campo: str) -> str:
    """
    Define el tipo esperado para cada campo, según la plantilla.
    """
    campos_lista = ["portales", "categoria"]
    campos_lista_dict = ["tipo_ayuda", "cuantia", "importe_maximo", "documentos_presentar"]
    campos_dict = ["lugares_presentacion", "administracion", "usuario", "resolucion", "publicacion_normativa"]

    if campo in campos_lista:
        return "list"
    elif campo in campos_lista_dict:
        return "list[dict]"
    elif campo in campos_dict:
        return "dict"
    else:
        return "str"

def asegurar_tipo_correcto(campo: str, valor: Union[str, list, dict]) -> Union[str, list, dict]:
    """
    Verifica que el valor coincida con el tipo esperado del campo.
    Si no, intenta transformarlo o devuelve un valor vacío.
    """
    tipo_esperado = tipo_esperado_por_campo(campo)

    if tipo_esperado == "list" and isinstance(valor, str):
        # Intentar parsear por comas o saltos
        candidatos = [v.strip() for v in re.split(r"[,\n]", valor) if v.strip()]
        return candidatos if candidatos else []

    if tipo_esperado == "list[dict]":
        if isinstance(valor, list) and all(isinstance(i, dict) for i in valor):
            return valor
        try:
            parsed = json.loads(valor) if isinstance(valor, str) else valor
            if isinstance(parsed, dict) and "tipo_ayuda" in parsed:
                return parsed["tipo_ayuda"]
            elif isinstance(parsed, list) and all(isinstance(i, dict) for i in parsed):
                return parsed
        except:
            pass
        return []

    if tipo_esperado == "dict":
        if isinstance(valor, dict):
            return valor
        if isinstance(valor, str):
            try:
                posible = json.loads(valor)
                return posible if isinstance(posible, dict) else {}
            except:
                return {}

    if tipo_esperado == "str":
        return str(valor).strip()

    return valor  # fallback

def validar_y_corregir_campo(campo: str, respuesta_cruda: str) -> Union[str, list, dict]:
    """
    Validación completa: limpia, parsea y ajusta tipo final según la plantilla.
    """
    valor = validar_y_limpiar_campo(respuesta_cruda)
    return asegurar_tipo_correcto(campo, valor)
