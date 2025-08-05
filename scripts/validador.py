
import re
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar tipos válidos desde JSON externo
with open(os.path.join(BASE_DIR, "..", "entradas", "tipos_ayuda.json"), encoding="utf-8") as f:
    TIPOS_AYUDA_VALIDOS = set(json.load(f)["tipos_de_ayuda"])

def esta_vacio(valor):
    if valor in ["", None, [], "- "]:
        return True
    if isinstance(valor, str) and not valor.strip():
        return True
    if isinstance(valor, list) and all(esta_vacio(e) for e in valor):
        return True
    if isinstance(valor, dict) and all(esta_vacio(v) for v in valor.values()):
        return True
    return False

def contiene_euros(texto):
    return bool(re.search(r"\d[\d\s]*[,\.]?\d*\s*€", texto))

def evaluar_json_por_reglas(json_data):
    resultado = {}
    score_total = 0
    campos_evaluados = 0

    def add_result(campo, valido, motivo=None):
        nonlocal score_total, campos_evaluados
        campos_evaluados += 1
        resultado[campo] = {"valido": valido}
        if valido:
            score_total += 1
        elif motivo:
            resultado[campo]["motivo"] = motivo

    # tipo_ayuda
    tipo_ayuda = json_data.get("tipo_ayuda", [])
    valido = all(t in TIPOS_AYUDA_VALIDOS for t in tipo_ayuda)
    add_result("tipo_ayuda", valido, "Contiene términos no válidos" if not valido else None)

    # descripcion
    descripcion = json_data.get("descripcion", "")
    valido = len(descripcion.split()) > 50 and not contiene_euros(descripcion)
    add_result("descripcion", valido, "Muy corta o contiene valores económicos")

    # referencia_legislativa
    ref = json_data.get("referencia_legislativa", "")
    valido = isinstance(ref, str) and ref.strip().startswith("- ") and ref.strip().endswith(".") and "\n" in ref
    add_result("referencia_legislativa", valido, "Debe ser lista multilínea con guiones y punto final")

    # cuantia
    cuantia = json_data.get("cuantia", [])
    cuantia_ok = any(e.get("valor") and not esta_vacio(e.get("unidad")) for e in cuantia if isinstance(e, dict))
    add_result("cuantia", cuantia_ok, "No contiene valores claros o unidades")

    # lugares_presentacion.online incluye Red SARA
    online = json_data.get("lugares_presentacion", {}).get("online", [])
    sara_ok = any("Red SARA" in e.get("valor", "") for e in online if isinstance(e, dict))
    add_result("lugares_presentacion.online", sara_ok, "Falta mención obligatoria a Red SARA")

    # usuario
    usuario = json_data.get("usuario", "")
    valido = bool(usuario and usuario.upper() not in ["USUARIO", "FICHAS MIGUEL"])
    add_result("usuario", valido, "Valor genérico o vacío")

    # documentos_presentar
    docs = json_data.get("documentos_presentar", [])
    doc_ok = sum(1 for d in docs if d.get("clave") and d.get("valor")) >= 2
    add_result("documentos_presentar", doc_ok, "Menos de 2 documentos completos")

    # requisitos_acceso como lista lógica
    req = json_data.get("requisitos_acceso", "")
    puntos = [x for x in re.split(r"[\n\-\•]+", req) if len(x.strip()) > 20]
    req_ok = len(puntos) >= 2
    add_result("requisitos_acceso", req_ok, "No está estructurado como lista clara")

    # frase_publicitaria
    frase = json_data.get("frase_publicitaria", "")
    if frase:
        valido = len(frase.split()) <= 30
        add_result("frase_publicitaria", valido, "Supera 30 palabras")
    else:
        add_result("frase_publicitaria", False, "Campo vacío")

    resultado["score_total"] = round(score_total / campos_evaluados, 2) if campos_evaluados else 0.0
    return resultado
