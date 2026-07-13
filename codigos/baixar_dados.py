import os
import requests
from bs4 import BeautifulSoup

def baixar_arquivo(url, pasta_destino):
    """Baixa um arquivo de uma URL para uma pasta específica."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        nome_arquivo = url.split("/")[-1]
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        with open(caminho_arquivo, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Download concluído: {nome_arquivo}")
    else:
        print(f"Erro ao baixar {url}: Status {response.status_code}")

def obter_links_csv(url_base):
    """Obtém todos os links de arquivos CSV em uma página FTP."""
    response = requests.get(url_base)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [url_base + a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.csv')]
        return links
    else:
        print(f"Erro ao acessar {url_base}: Status {response.status_code}")
        return []

def baixar_dados():
    """Baixa os arquivos dos últimos 2 anos dos links especificados."""
    urls = [
        "fontesecreta",
        "fontesecreta"
    ]
    
    pasta_destino = "dados_ans"
    os.makedirs(pasta_destino, exist_ok=True)
    
    for url_base in urls:
        links_csv = obter_links_csv(url_base)
        for link in links_csv:
            baixar_arquivo(link, pasta_destino)

if __name__ == "__main__":
    baixar_dados()
