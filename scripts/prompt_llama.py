import requests
import json

# Cargar plantilla JSON desde archivo
def cargar_plantilla_json(path="scripts/plantilla.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Generar el prompt con instrucciones estrictas
def generar_prompt(texto_pdf, plantilla_json):
    opciones = json.dumps(plantilla_json, indent=2, ensure_ascii=False)
    prompt = f"""
Analiza el siguiente texto de una ayuda legal.

Devuelve un JSON con esta estructura exacta, rellenando solo los campos para los que tengas información clara o contexto suficiente. Si no puedes inferir un dato con seguridad, **déjalo vacío**.

 No inventes información.
 No añadas campos nuevos.
 Usa exactamente la estructura del JSON proporcionado.

Campos como "portales", "categoria" y "tipo_ayuda" deben seleccionarse solo de entre las opciones dadas, aunque no aparezcan literalmente si el contexto lo justifica.

Texto del documento:
{texto_pdf}

Estructura JSON a completar:
{opciones}
"""
    return prompt.strip()

# Llamar al servidor de Ollama con temperatura reducida
def llamar_ollama(prompt, modelo="llama3", temperatura=0.2):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": modelo,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperatura
            }
        }
    )
    response.raise_for_status()
    data = response.json()
    return json.loads(data["response"])

# Para ejecución directa
if __name__ == "__main__":
    import sys

    # Leer texto del PDF desde stdin
    texto_pdf = sys.stdin.read()

    # Cargar plantilla JSON
    plantilla = cargar_plantilla_json()

    # Generar el prompt
    prompt = generar_prompt(texto_pdf, plantilla)

    # Llamar a la IA
    resultado_json = llamar_ollama(prompt)

    # Imprimir JSON de salida formateado
    print(json.dumps(resultado_json, indent=2, ensure_ascii=False))
