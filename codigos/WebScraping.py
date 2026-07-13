import os
import subprocess
import sys

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

from zipfile import ZipFile

# Diretório onde os arquivos serão salvos
output_dir = 'anexos'
os.makedirs(output_dir, exist_ok=True)

# URLs dos anexos
anexos = {
    'Anexo I': 'basededadosgenerica I.pdf',
    'Anexo II': 'basededadosgenerica II.pdf'
}

headers = {'User-Agent': 'Mozilla/5.0'}

# Baixar os anexos
for nome, url in anexos.items():
    response = requests.get(url, headers=headers, stream=True, timeout=60)
    if response.status_code == 200:
        file_path = os.path.join(output_dir, f'{nome}.pdf')
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'{nome} baixado com sucesso.')
    else:
        print(f'Falha ao baixar {nome}. Status: {response.status_code}')

# Compactar os anexos em um arquivo ZIP
zip_path = os.path.join(output_dir, 'anexos.zip')
with ZipFile(zip_path, 'w') as zipf:
    for nome in anexos.keys():
        file_path = os.path.join(output_dir, f'{nome}.pdf')
        if os.path.exists(file_path):
            zipf.write(file_path, os.path.basename(file_path))
            print(f'{nome} adicionado ao arquivo ZIP.')

print(f'Arquivo ZIP criado em: {zip_path}')
