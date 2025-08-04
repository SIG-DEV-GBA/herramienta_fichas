import logging
from scripts.extract_text import extract_text_from_pdf
from scripts.prompt_builder import build_prompts
from scripts.call_mistral import llamar_mistral


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# === FLUJO PRINCIPAL ===

try:
    # Paso 1: Extraer texto del PDF
    ruta_pdf = "entradas/documentos/ejemplo.pdf"
    logging.info(f"Extrayendo texto desde: {ruta_pdf}")
    texto = extract_text_from_pdf(ruta_pdf)

    # NUEVO: Guardar texto extraído para chunker
    with open("entradas/documentos/ejemplo_extraido.txt", "w", encoding="utf-8") as f:
        f.write(texto)

    # Paso 2: Construir prompts desde plantilla + instrucciones
    ruta_plantilla = "entradas/plantilla.json"
    ruta_instrucciones = "entradas/intrucciones.json"
    logging.info("Cargando plantilla e instrucciones para construir el prompt...")
    system_prompt, user_prompt = build_prompts(texto, ruta_plantilla, ruta_instrucciones)

    # Paso 3: Llamar a Ollama con el prompt generado
    respuesta = llamar_mistral(system_prompt, user_prompt, nombre_salida="respuesta_mistral")


    # Paso 4: Mostrar parte del resultado
    if respuesta is not None:
        print("\n--- RESPUESTA DE MISTRAL 7B ---\n")
        print(str(respuesta)[:1000])
    else:
        print("❌ No se recibió ninguna respuesta válida del modelo.")

except Exception as e:
    logging.exception(f"Error inesperado durante la ejecución: {e}")
