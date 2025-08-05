import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Función para cargar plantilla vacía
def cargar_plantilla_vacia():
    with open(os.path.join(BASE_DIR, "..", "entradas", "plantilla.json"), "r", encoding="utf-8") as f:
        return json.load(f)

# Función genérica para combinar listas, con normalización de strings y eliminación de vacíos
def combinar_listas(lista1, lista2, clave_identificadora=None):
    if not isinstance(lista1, list):
        lista1 = []
    if not isinstance(lista2, list):
        lista2 = []

    def normalizar_string(s):
        return s.strip().replace('"', '').replace("\\\"", "").strip()

    if clave_identificadora:
        existentes = {normalizar_string(elem[clave_identificadora]) for elem in lista1 if clave_identificadora in elem and elem[clave_identificadora].strip()}
        nuevos = [elem for elem in lista2 if normalizar_string(elem.get(clave_identificadora, '')) not in existentes and any(v.strip() for v in elem.values())]
        return lista1 + nuevos
    else:
        total = set(normalizar_string(e) for e in lista1 if isinstance(e, str) and e.strip())
        total.update(normalizar_string(e) for e in lista2 if isinstance(e, str) and e.strip())
        return list(total)

# Funciones específicas de fusión por campo
def fusionar_referencia_legislativa(actual, nuevo):
    return combinar_listas(actual, nuevo)

def fusionar_cuantia(actual, nuevo):
    return combinar_listas(actual, nuevo, "concepto")

def fusionar_importe_maximo(actual, nuevo):
    return combinar_listas(actual, nuevo, "concepto")

def fusionar_documentos_presentar(actual, nuevo):
    return combinar_listas(actual, nuevo, "clave")

def fusionar_listas_simples(actual, nuevo):
    return combinar_listas(actual, nuevo)

def fusionar_lugares_presentacion(actual, nuevo):
    for tipo in ["presencial", "online"]:
        actual[tipo] = combinar_listas(actual.get(tipo, []), nuevo.get(tipo, []), "clave")
    return actual

FUSIONADORES = {
    "referencia_legislativa": fusionar_referencia_legislativa,
    "cuantia": fusionar_cuantia,
    "importe_maximo": fusionar_importe_maximo,
    "documentos_presentar": fusionar_documentos_presentar,
    "portales": fusionar_listas_simples,
    "categoria": fusionar_listas_simples,
    "tipo_ayuda": fusionar_listas_simples,
    "lugares_presentacion": fusionar_lugares_presentacion,
}

# Refuerzo obligatorio de valores mínimos al final de la fusión
def completar_minimos_obligatorios(json_final):
    if not json_final.get("referencia_legislativa") or json_final["referencia_legislativa"] == "- ":
        json_final["referencia_legislativa"] = "- Ley 38/2003, de 17 de noviembre, General de Subvenciones."

    if not json_final.get("lugares_presentacion"):
        json_final["lugares_presentacion"] = {"presencial": [], "online": []}

    if not json_final["lugares_presentacion"].get("presencial"):
        json_final["lugares_presentacion"]["presencial"] = [{
            "clave": "Presencialmente en:",
            "valor": "Oficinas de correos para Registro de documentos según procedimiento administrativo (con el sobre abierto para compulsa de documentos). Registro de Ventanilla Única en el territorio Nacional."
        }]

    if not json_final["lugares_presentacion"].get("online"):
        json_final["lugares_presentacion"]["online"] = [{
            "clave": "Electrónicamente en:",
            "valor": "También puede presentarse a través de la Red SARA (Sistema de Aplicaciones y Redes para las Administraciones), una plataforma estatal segura que permite enviar solicitudes electrónicas a cualquier administración pública, usando certificado digital o sistema Cl@ve."
        }]

    if json_final.get("usuario", "").strip().upper() in ["USUARIO", "FICHAS MIGUEL"]:
        json_final["usuario"] = "MELIANA"

# Función principal para fusionar varios JSONs
def fusionar_jsons(nombre_base):
    carpeta = os.path.join(BASE_DIR, "..", "salidas_json")
    archivos = [
        os.path.join(carpeta, f) for f in os.listdir(carpeta)
        if f.startswith(nombre_base + "_parte") and f.endswith(".json")
    ]

    if not archivos:
        print("❌ No se encontraron partes JSON a fusionar.")
        return

    json_final = cargar_plantilla_vacia()

    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"📥 Procesando: {archivo}")

            for clave, valor in data.items():
                if not valor or valor in ["- ", ""]:
                    continue
                if clave not in json_final or not json_final[clave]:
                    json_final[clave] = valor
                elif isinstance(valor, list) or isinstance(valor, dict):
                    fusionador = FUSIONADORES.get(clave)
                    if fusionador:
                        json_final[clave] = fusionador(json_final[clave], valor)

        except Exception as e:
            print(f"[ERROR] Fallo al procesar {archivo}: {e}")

    completar_minimos_obligatorios(json_final)

    ruta_salida = os.path.join(carpeta, f"{nombre_base}_fusionado.json")
    try:
        with open(ruta_salida, "w", encoding="utf-8") as f:
            json.dump(json_final, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON fusionado guardado en: {ruta_salida}")
    except Exception as e:
        print(f"❌ Error al guardar el JSON fusionado: {e}")

# CLI opcional
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python fusionador.py <nombre_base>")
    else:
        fusionar_jsons(sys.argv[1])
