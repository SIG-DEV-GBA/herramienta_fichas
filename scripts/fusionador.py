
import os
import json
from validador import evaluar_json_por_reglas, esta_vacio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def cargar_plantilla_vacia():
    with open(os.path.join(BASE_DIR, "..", "entradas", "plantilla.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def normalizar_str(s):
    return s.strip().lower().replace('"', '')

def fusionar_texto_mejorado(versiones):
    versiones_filtradas = [v.strip() for v in versiones if not esta_vacio(v)]
    if not versiones_filtradas:
        return ""
    return max(versiones_filtradas, key=lambda x: len(x))

def fusionar_lista_simple(versiones):
    resultado = set()
    for lista in versiones:
        resultado.update([normalizar_str(i) for i in lista if i and isinstance(i, str)])
    return sorted(resultado)

def fusionar_lista_dict(versiones, clave):
    vistos = set()
    resultado = []
    for lista in versiones:
        for item in lista:
            id_val = normalizar_str(item.get(clave, ""))
            if id_val and id_val not in vistos and not esta_vacio(item):
                resultado.append(item)
                vistos.add(id_val)
    return resultado

def fusionar_referencia_legislativa(versiones):
    lineas = set()
    for entrada in versiones:
        for linea in entrada.strip().split("\n"):
            linea = linea.strip()
            if linea.startswith("- ") and linea.endswith("."):
                lineas.add(linea)
    return "\n".join(sorted(lineas))

def fusionar_campo(clave, versiones):
    if not versiones:
        return None
    if clave in ["descripcion", "resolucion", "costes_no_subvencionables", "criterios_concesion"]:
        return fusionar_texto_mejorado(versiones)
    if clave in ["portales", "categoria", "tipo_ayuda"]:
        return fusionar_lista_simple(versiones)
    if clave in ["cuantia", "importe_maximo", "documentos_presentar"]:
        return fusionar_lista_dict(versiones, "concepto" if clave != "documentos_presentar" else "clave")
    if clave == "referencia_legislativa":
        return fusionar_referencia_legislativa(versiones)
    if clave == "lugares_presentacion":
        final = {"presencial": [], "online": []}
        for v in versiones:
            for tipo in ["presencial", "online"]:
                final[tipo].extend([i for i in v.get(tipo, []) if not esta_vacio(i)])
        for tipo in final:
            vistos = set()
            final[tipo] = [d for d in final[tipo] if normalizar_str(d.get("valor", "")) not in vistos and not vistos.add(normalizar_str(d.get("valor", "")))]
        return final
    return fusionar_texto_mejorado(versiones)

def fusionar_jsons(nombre_base):
    carpeta = os.path.join(BASE_DIR, "..", "salidas_json")
    archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.startswith(nombre_base + "_parte") and f.endswith(".json")]
    if not archivos:
        print("❌ No se encontraron partes JSON a fusionar.")
        return

    json_final = cargar_plantilla_vacia()
    versiones_por_campo = {clave: [] for clave in json_final.keys()}

    for archivo in archivos:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        validacion = evaluar_json_por_reglas(data)
        for clave, valor in data.items():
            if not esta_vacio(valor) and validacion.get(clave, {}).get("valido", True):
                versiones_por_campo[clave].append(valor)

    for clave, versiones in versiones_por_campo.items():
        json_final[clave] = fusionar_campo(clave, versiones)

    ruta_salida = os.path.join(carpeta, f"{nombre_base}_fusionado.json")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(json_final, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON fusionado guardado en: {ruta_salida}")
