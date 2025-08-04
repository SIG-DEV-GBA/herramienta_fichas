import logging
import json
from scripts.extract_text import extract_text_from_pdf, chunk_text
from scripts.embedding_manager import generar_embeddings
from scripts.generador_ficha import rellenar_ficha, guardar_ficha
from scripts.verificador_ficha import verificar_ficha_vs_plantilla
from scripts.exportar_ficha_docx import exportar_ficha_legible_a_docx

# Configurar logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === CONFIGURACIÓN INICIAL ===
RUTA_PDF = "entradas/documentos/ejemplo.pdf"
DOC_ID = "documento_001"
ARCHIVO_SALIDA = f"salidas/ficha_{DOC_ID}.json"
ARCHIVO_PLANTILLA = "entradas/plantilla.json"
ARCHIVO_DOCX = f"salidas/ficha_legible_{DOC_ID}.docx"

def main():
    logging.info("🟦 Inicio del proceso de generación de ficha legal")

    # === PASO 1: EXTRAER TEXTO DEL PDF ===
    texto = extract_text_from_pdf(RUTA_PDF)
    if not texto:
        logging.error("❌ No se pudo extraer texto del PDF. Terminando.")
        return

    # === PASO 2: DIVIDIR TEXTO EN CHUNKS ===
    chunks = chunk_text(texto)

    # === PASO 3: CREAR Y GUARDAR EMBEDDINGS ===
    generar_embeddings(chunks, doc_id=DOC_ID)

    # === PASO 4: RELLENAR CAMPOS DEL JSON CON GPT ===
    ficha = rellenar_ficha(doc_id=DOC_ID)

    # === PASO 5: GUARDAR RESULTADO COMO JSON ===
    guardar_ficha(ficha, ARCHIVO_SALIDA)

    # === PASO 6: VERIFICAR CONTRA PLANTILLA ===
    try:
        with open(ARCHIVO_PLANTILLA, "r", encoding="utf-8") as f:
            plantilla = json.load(f)

        errores = verificar_ficha_vs_plantilla(plantilla, ficha)

        if not errores:
            logging.info("✅ Verificación final: ficha estructuralmente correcta.")
        else:
            logging.warning("🔎 Informe de verificación:")
            for err in errores:
                print(f" - {err}")
    except Exception as e:
        logging.error(f"Error durante la verificación: {e}")

    # === PASO 7: EXPORTAR A DOCUMENTO LEGIBLE ===
    exportar_ficha_legible_a_docx(ARCHIVO_SALIDA, ARCHIVO_DOCX)
    logging.info(f"📄 Documento Word generado en: {ARCHIVO_DOCX}")

    # Vista previa parcial
    print("\n🟢 FICHA GENERADA:\n")
    print(json.dumps(ficha, indent=2, ensure_ascii=False)[:2000])

if __name__ == "__main__":
    main()
