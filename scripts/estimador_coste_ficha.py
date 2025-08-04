import json
import matplotlib.pyplot as plt
import pandas as pd
import tiktoken
from pathlib import Path

# Configuración por modelo
modelo = "gpt-4o"
precios_por_1k = {
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4-1106-preview": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
}

# Ruta al JSON generado (ficha completa)
RUTA_JSON = "salidas/ficha_documento_001.json"

# Elegir codificador de tokens según modelo
encoding = tiktoken.encoding_for_model(modelo)

# Cargar el JSON
with open(RUTA_JSON, "r", encoding="utf-8") as f:
    ficha = json.load(f)

# Contadores
tokens_entrada_total = 0
tokens_salida_total = 0

# Simulación: por cada campo, se pasa X texto de contexto y se espera Y de respuesta
tokens_entrada_promedio_por_prompt = 1200  # ajustable si usas menos chunks
for campo, valor in ficha.items():
    tokens_entrada_total += tokens_entrada_promedio_por_prompt
    texto_salida = json.dumps(valor) if isinstance(valor, (dict, list)) else str(valor)
    tokens_salida_total += len(encoding.encode(texto_salida))

# Calcular coste estimado
precio = precios_por_1k[modelo]
coste_entrada = (tokens_entrada_total / 1000) * precio["input"]
coste_salida = (tokens_salida_total / 1000) * precio["output"]
coste_total = coste_entrada + coste_salida

# Mostrar resumen
df = pd.DataFrame({
    "Concepto": [
        "Tokens de entrada",
        "Tokens de salida",
        "Total tokens",
        "Coste entrada ($)",
        "Coste salida ($)",
        "Coste total estimado ($)"
    ],
    "Valor": [
        tokens_entrada_total,
        tokens_salida_total,
        tokens_entrada_total + tokens_salida_total,
        round(coste_entrada, 5),
        round(coste_salida, 5),
        round(coste_total, 5)
    ]
})

print("\n📊 Estimación de coste por ficha legal:\n")
print(df.to_string(index=False))

# Gráfico
plt.figure(figsize=(6, 4))
plt.bar(["Entrada", "Salida"], [coste_entrada, coste_salida], color=["#4CAF50", "#2196F3"])
plt.title(f"Coste estimado por ficha - {modelo}")
plt.ylabel("USD $")
for i, v in enumerate([coste_entrada, coste_salida]):
    plt.text(i, v + 0.001, f"${v:.4f}", ha='center', va='bottom')
plt.tight_layout()
plt.show()
