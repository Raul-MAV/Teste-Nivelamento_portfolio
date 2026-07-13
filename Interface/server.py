from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir requisições do frontend

# Carregar o CSV na memória
df = pd.read_csv('Relatorio_cadop.csv', sep=';', dtype=str)

@app.route('/operadoras', methods=['GET'])
def buscar_operadoras():
    termo = request.args.get('nome', '').lower()
    if not termo:
        return jsonify([])  # Retorna uma lista vazia se nenhum termo for fornecido

    # Filtrar registros que contenham o termo no campo 'Razao_Social'
    resultados = df[df['Razao_Social'].str.lower().str.contains(termo, na=False)]

    # Selecionar apenas os campos necessários para o frontend
    campos = ['Registro_ANS', 'Razao_Social', 'Cidade', 'UF']
    resultados = resultados[campos]

    # Retornar os 10 primeiros resultados como JSON
    return jsonify(resultados.head(10).to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)