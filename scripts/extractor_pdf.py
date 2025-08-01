import fitz  
import sys

def extraer_texto_pdf(ruta_pdf):
    doc = fitz.open(ruta_pdf)
    texto = ""
    for pagina in doc:
        texto += pagina.get_text()
    doc.close()
    return texto.strip()

if __name__ == "__main__":
    ruta_pdf = sys.argv[1]
    print(extraer_texto_pdf(ruta_pdf))
