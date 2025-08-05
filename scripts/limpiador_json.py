
import re

def normalizar_concepto(texto):
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9áéíóúñü\s]", "", texto)
    texto = re.sub(r"\bdel?\b|\bpara\b|\bcon\b|\bla\b|\blas\b|\bde\b|\bpor\b", "", texto)
    return re.sub(r"\s+", " ", texto).strip()

def limpiar_cuantia(json_data):
    vistos = set()
    nuevas_cuantias = []
    for item in json_data.get("cuantia", []):
        concepto_norm = normalizar_concepto(item.get("concepto", ""))
        valor = item.get("valor", "").strip()
        unidad = item.get("unidad", "").strip()
        if not concepto_norm or not valor:
            continue
        clave = f"{concepto_norm}:{valor}"
        if clave not in vistos:
            nuevas_cuantias.append(item)
            vistos.add(clave)
    json_data["cuantia"] = nuevas_cuantias

def corregir_lugares_presentacion(json_data):
    if "lugares_presentacion" not in json_data:
        json_data["lugares_presentacion"] = {"presencial": [], "online": []}

    presencial = json_data["lugares_presentacion"].get("presencial", [])
    online = json_data["lugares_presentacion"].get("online", [])

    # Añadir oficina de correos si falta
    correos = "Oficinas de correos para Registro de documentos según procedimiento administrativo"
    if not any(correos.lower() in e.get("valor", "").lower() for e in presencial):
        presencial.append({
            "clave": "Presencialmente en:",
            "valor": f"{correos} (con el sobre abierto para compulsa de documentos). Registro de Ventanilla Única en el territorio Nacional."
        })

    # Añadir sede electrónica si falta
    sede_url = "https://meliana.sede.dival.es/"
    if not any(sede_url in e.get("valor", "") for e in online):
        online.insert(0, {
            "clave": "Electrónicamente en:",
            "valor": f"{sede_url}. También puede presentarse a través de la Red SARA (Sistema de Aplicaciones y Redes para las Administraciones), una plataforma estatal segura que permite enviar solicitudes electrónicas a cualquier administración pública, usando certificado digital o sistema Cl@ve."
        })

    json_data["lugares_presentacion"]["presencial"] = presencial
    json_data["lugares_presentacion"]["online"] = online

def sanear_json_final(json_data):
    limpiar_cuantia(json_data)
    corregir_lugares_presentacion(json_data)
    return json_data
