from scripts.resumidor_test import generar_resumen

def main():
    with open("entradas/documentos/ejemplo_extraido.txt", "r", encoding="utf-8") as f:
        texto = f.read()

    resultado = generar_resumen(texto)
    print(resultado)

if __name__ == "__main__":
    main()
