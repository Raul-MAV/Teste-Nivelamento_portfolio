import os
import requests
import zipfile
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
import sqlite3
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_SCRIPT_DIR, "dados_ans", "ans_dados.db")
_PASTA_DADOS = os.path.join(_SCRIPT_DIR, "dados_ans")

def baixar_arquivo(url, caminho_destino):
    """Baixa um arquivo de uma URL para um caminho específico."""
    response = requests.get(url, stream=True, timeout=60)
    if response.status_code == 200:
        with open(caminho_destino, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Download concluído: {os.path.basename(caminho_destino)}")
        return True
    else:
        print(f"Erro ao baixar {url}: Status {response.status_code}")
        return False

def obter_links(url_base, extensao):
    """Obtém links de arquivos com determinada extensão em uma página."""
    response = requests.get(url_base, timeout=30)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return [url_base + a['href'] for a in soup.find_all('a', href=True)
                if a['href'].endswith(extensao)]
    return []

def baixar_dados():
    """Baixa os arquivos dos últimos 2 anos e o cadastro de operadoras."""
    pasta_destino = _PASTA_DADOS
    os.makedirs(pasta_destino, exist_ok=True)

    # Demonstrativos contábeis: últimos 2 anos em ZIP
    ano_atual = datetime.now().year
    base_url = "fontesecreta"
    for ano in [ano_atual - 1, ano_atual - 2]:
        links = obter_links(f"{base_url}{ano}/", ".zip")
        for link in links:
            nome = os.path.basename(link)
            caminho_zip = os.path.join(pasta_destino, nome)
            if not os.path.exists(caminho_zip):
                if baixar_arquivo(link, caminho_zip):
                    with zipfile.ZipFile(caminho_zip, 'r') as z:
                        z.extractall(pasta_destino)
                        print(f"Extraído: {nome}")

    # Operadoras ativas
    url_op = "fontesecreta"
    links_csv = obter_links(url_op, ".csv")
    for link in links_csv:
        nome = os.path.basename(link)
        caminho = os.path.join(pasta_destino, nome)
        if not os.path.exists(caminho):
            baixar_arquivo(link, caminho)

def conectar_banco():
    """Conecta ao banco de dados SQLite."""
    conexao = sqlite3.connect(DB_PATH)
    return conexao

def importar_csv_para_banco():
    """Importa os arquivos CSV baixados para o banco de dados."""
    pasta_destino = _PASTA_DADOS
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Importar demonstrativos contábeis (todos os CSVs extraídos dos ZIPs)
    dfs = []
    for f in os.listdir(pasta_destino):
        if f.endswith(".csv") and f != "Relatorio_cadop.csv":
            caminho = os.path.join(pasta_destino, f)
            try:
                df = pd.read_csv(caminho, delimiter=';', encoding='latin-1', dtype=str)
                dfs.append(df)
                print(f"Lido: {f} ({len(df)} linhas)")
            except Exception as e:
                print(f"Erro ao ler {f}: {e}")
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        df_all.to_sql("demonstrativos_contabeis", engine, if_exists='replace', index=False)
        print(f"Demonstrativos importados: {len(df_all)} linhas no total")
    else:
        print("Nenhum CSV de demonstrativos encontrado.")

    # Importar operadoras ativas
    cadop = os.path.join(pasta_destino, "Relatorio_cadop.csv")
    if os.path.exists(cadop):
        try:
            df_op = pd.read_csv(cadop, delimiter=';', encoding='latin-1', dtype=str)
            df_op.to_sql("operadoras_ativas", engine, if_exists='replace', index=False)
            print(f"Operadoras importadas: {len(df_op)} linhas")
        except Exception as e:
            print(f"Erro ao importar operadoras: {e}")
    else:
        print("Arquivo Relatorio_cadop.csv não encontrado!")

def executar_consultas():
    """Executa consultas analíticas para encontrar as operadoras com maiores despesas."""
    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Descobrir colunas reais da tabela
    try:
        cursor.execute("PRAGMA table_info(demonstrativos_contabeis)")
        colunas = [row[1] for row in cursor.fetchall()]
        print(f"\nColunas em demonstrativos_contabeis: {colunas}\n")
    except Exception:
        colunas = []

    if not colunas:
        print("Tabela demonstrativos_contabeis vazia ou não encontrada.")
        conexao.close()
        return

    # Detectar nomes de colunas comuns no dataset ANS
    col_reg = next((c for c in colunas if 'REG' in c.upper() and 'ANS' in c.upper()), colunas[0])
    col_desc = next((c for c in colunas if 'DESCRI' in c.upper()), None)
    col_valor = next((c for c in colunas if 'SALDO_FINAL' in c.upper() or 'VL_' in c.upper()), None)
    col_data = next((c for c in colunas if 'DATA' in c.upper()), None)

    if not all([col_desc, col_valor, col_data]):
        print("Colunas necessárias não encontradas. Exibindo amostra dos dados:")
        cursor.execute("SELECT * FROM demonstrativos_contabeis LIMIT 3")
        for row in cursor.fetchall():
            print(row)
        conexao.close()
        return

    ano_atual = datetime.now().year

    # Descobrir o trimestre mais recente disponível no banco
    cursor.execute("SELECT MAX(DATA) FROM demonstrativos_contabeis")
    max_data = cursor.fetchone()[0] or ""
    if max_data and len(max_data) >= 7:
        ano_recente = int(max_data[:4])
        # Suporta tanto YYYYMMDD quanto YYYY-MM-DD
        if max_data[4] == "-":
            mes_recente = int(max_data[5:7])
        else:
            mes_recente = int(max_data[4:6])
        trimestre_recente = (mes_recente - 1) // 3 + 1
        mes_inicio = (trimestre_recente - 1) * 3 + 1
        mes_fim = trimestre_recente * 3
        # Detectar formato para usar na query SQL
        if max_data[4] == "-":
            substr_mes = f'CAST(substr("{col_data}", 6, 2) AS INTEGER)'
            substr_ano = f'CAST(substr("{col_data}", 1, 4) AS INTEGER)'
        else:
            substr_mes = f'CAST(substr("{col_data}", 5, 2) AS INTEGER)'
            substr_ano = f'CAST(substr("{col_data}", 1, 4) AS INTEGER)'
        filtro_trimestre = (
            f'{substr_ano} = {ano_recente} '
            f'AND {substr_mes} BETWEEN {mes_inicio} AND {mes_fim}'
        )
        filtro_ano = f'{substr_ano} = {ano_recente}'
        label_trimestre = f"{trimestre_recente}T{ano_recente}"
    else:
        mes_atual = datetime.now().month
        trimestre_atual = (mes_atual - 1) // 3 + 1
        ano_recente = datetime.now().year - 1
        mes_inicio = (trimestre_atual - 1) * 3 + 1
        mes_fim = trimestre_atual * 3
        substr_mes = f'CAST(substr("{col_data}", 6, 2) AS INTEGER)'
        substr_ano = f'CAST(substr("{col_data}", 1, 4) AS INTEGER)'
        filtro_trimestre = (
            f'{substr_ano} = {ano_recente} '
            f'AND {substr_mes} BETWEEN {mes_inicio} AND {mes_fim}'
        )
        filtro_ano = f'{substr_ano} = {ano_recente}'
        label_trimestre = f"{trimestre_atual}T{ano_recente}"

    # Consulta para o trimestre mais recente disponível
    consulta_trimestre = f"""
        SELECT "{col_reg}", SUM(CAST(REPLACE(REPLACE("{col_valor}", '.', ''), ',', '.') AS REAL)) AS total_despesas
        FROM demonstrativos_contabeis
        WHERE "{col_desc}" LIKE '%SINISTROS%ASSIST%'
          AND {filtro_trimestre}
        GROUP BY "{col_reg}"
        ORDER BY total_despesas DESC
        LIMIT 10
    """
    cursor.execute(consulta_trimestre)
    print(f"Top 10 operadoras com maiores despesas no último trimestre disponível ({label_trimestre}):")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("  (sem dados para o período)")

    # Consulta para o último ano completo disponível
    consulta_ano = f"""
        SELECT "{col_reg}", SUM(CAST(REPLACE(REPLACE("{col_valor}", '.', ''), ',', '.') AS REAL)) AS total_despesas
        FROM demonstrativos_contabeis
        WHERE "{col_desc}" LIKE '%SINISTROS%ASSIST%'
          AND {filtro_ano}
        GROUP BY "{col_reg}"
        ORDER BY total_despesas DESC
        LIMIT 10
    """
    cursor.execute(consulta_ano)
    print(f"\nTop 10 operadoras com maiores despesas em {ano_recente}:")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("  (sem dados para o período)")

    conexao.close()

if __name__ == "__main__":
    try:
        baixar_dados()
        importar_csv_para_banco()
        executar_consultas()
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        raise