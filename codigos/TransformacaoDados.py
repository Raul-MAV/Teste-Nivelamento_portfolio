import os
import zipfile
import pdfplumber  # type: ignore
import pandas as pd  # type: ignore

# Nome do arquivo PDF do Anexo I
pdf_file = "anexos/Anexo I.pdf"

# Nome do CSV e do ZIP
csv_file = "Teste_seu_nome.csv"
zip_file = "Teste_seu_nome.zip"

# Extração de dados do PDF
data = []
with pdfplumber.open(pdf_file) as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                # Limpar e padronizar os dados
                row = [cell.strip().replace('\n', ' ') if cell else "" for cell in row]
                
                # Ignorar cabeçalhos repetidos ou linhas que não fazem parte da tabela
                if "Código" in row[0] or "PROCEDIMENTO" in row[0]:
                    continue
                
                # Garantir que a linha tem ao menos 3 colunas válidas
                if sum(1 for cell in row if cell) >= 3:
                    data.append(row)

# Criar DataFrame
if data:
    expected_cols = ["Código", "Descrição", "RN", "Vigência", "OD", "AMB", "HCO", "HSO", "REF", "PAC", "DUT"]
    max_cols = len(expected_cols)
    
    # Padronizar o número de colunas em cada linha
    data = [row + [""] * (max_cols - len(row)) if len(row) < max_cols else row[:max_cols] for row in data]
    
    df = pd.DataFrame(data, columns=expected_cols)
    
    # Remover linhas completamente vazias
    df.dropna(how='all', inplace=True)
    
    # Substituir abreviações pelas descrições completas
    substituicoes = {
        "OD": "Seg. Odontológica",
        "AMB": "Seg. Ambulatorial",
        "HCO": "Seg. Hospitalar Com Obstetrícia",
        "HSO": "Seg. Hospitalar Sem Obstetrícia",
        "REF": "Plano Referência",
        "PAC": "Procedimento de Alta Complexidade",
        "DUT": "Diretriz de Utilização"
    }
    
    for coluna, descricao in substituicoes.items():
        if coluna in df.columns:
            df[coluna] = df[coluna].replace({coluna: descricao})
    
    # Preencher células vazias com string vazia para evitar delimitadores extras
    df.fillna("", inplace=True)
    
    # Salvar como CSV estruturado
    df.to_csv(csv_file, index=False, encoding='utf-8', sep=';')
    
    # Compactar CSV
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_file)
    
    print(f"Arquivo CSV salvo como {csv_file} e compactado como {zip_file}")
else:
    print("Nenhuma tabela válida encontrada no PDF.")
