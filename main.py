import os
import sys

# Ruta base = carpeta donde está este main.py (es decir, /dev)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Añadir la subcarpeta 'scripts' al path
sys.path.append(os.path.join(BASE_DIR, 'scripts'))

from scripts.extractor_texto import extraer_textos_unificados
from scripts.resumidor_ia import resumir_desde_varios_archivos
from scripts.fusionador import fusionar_jsons
from scripts.generar_docx import generar_docx_desde_json

def guardar_texto_como_txt(texto: str, nombre_base: str):
    ruta_txt = os.path.join(BASE_DIR, "salidas_txt", f"{nombre_base}_extraido.txt")
    os.makedirs(os.path.dirname(ruta_txt), exist_ok=True)
    try:
        with open(ruta_txt, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f"💾 Texto combinado guardado en: {ruta_txt}")
    except Exception as e:
        print(f"❌ Error al guardar el archivo .txt: {e}")

def guardar_respuesta_bruta(respuesta: str, nombre_base: str):
    ruta_log = os.path.join(BASE_DIR, "logs", f"{nombre_base}_respuesta_raw.txt")
    os.makedirs(os.path.dirname(ruta_log), exist_ok=True)
    try:
        with open(ruta_log, 'w', encoding='utf-8') as f:
            f.write(respuesta)
        print(f"📝 Respuesta bruta guardada en: {ruta_log}")
    except Exception as e:
        print(f"❌ Error al guardar la respuesta bruta: {e}")

def obtener_documentos_entrada() -> list[str]:
    carpeta = os.path.join(BASE_DIR, "entradas", "documentos")
    extensiones_validas = [".pdf", ".docx"]

    documentos = [
        os.path.join(carpeta, f)
        for f in sorted(os.listdir(carpeta))
        if os.path.isfile(os.path.join(carpeta, f)) and os.path.splitext(f)[1].lower() in extensiones_validas
    ]

    if not documentos:
        print("⚠️ No se encontraron documentos .pdf o .docx en la carpeta de entrada.")

    return documentos

def main():
    rutas_documentos = obtener_documentos_entrada()
    nombre_base = "ficha_unificada"

    if not rutas_documentos:
        return

    print("🟡 Documentos encontrados:")
    for ruta in rutas_documentos:
        print(f"   📄 {os.path.basename(ruta)}")
    print("\n🟡 Extrayendo y unificando texto...\n")

    from scripts.extractor_texto import extraer_textos_unificados
    texto_unificado = extraer_textos_unificados(rutas_documentos)

    if not texto_unificado.strip():
        print("❌ No se pudo extraer texto de los documentos.")
        return

    print("✅ Texto extraído con éxito. Guardando copia .txt...\n")
    guardar_texto_como_txt(texto_unificado, nombre_base)

    print("🤖 Generando resumen unificado con IA por chunks...\n")
    resumen_json = resumir_desde_varios_archivos(rutas_documentos, nombre_base)
    guardar_respuesta_bruta(resumen_json, nombre_base)

    print("🧬 Fusionando chunks en JSON final...\n")
    fusionar_jsons(nombre_base)

    json_path = os.path.join(BASE_DIR, "salidas_json", f"{nombre_base}_fusionado.json")

    if os.path.exists(json_path):
        print("📄 Generando documento Word...\n")
        generar_docx_desde_json(json_path)
    else:
        print(f"❌ No se encontró el JSON fusionado en {json_path}")

if __name__ == "__main__":
    main()
