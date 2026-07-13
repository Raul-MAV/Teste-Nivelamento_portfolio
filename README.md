Data Intelligence & Web Automation - Teste de Nivelamento
Este repositório reúne uma série de soluções modulares voltadas para automação web (Web Scraping), extração, processamento e transformação de dados, além do desenvolvimento de uma aplicação full-stack para busca de operadoras de saúde.  
MD

O projeto foi estruturado de forma agnóstica a dados confidenciais, utilizando mocks estruturais e variáveis de ambiente para demonstrar competências técnicas de engenharia de dados e desenvolvimento de software.  
MD

📂 Estrutura do Repositório
O projeto é dividido em 4 subfrentes principais (Teste1 a Teste4):

Bash
├── Teste1/
│   ├── WebScraping.py          # Automação e captura de documentos/dados via Python
│   └── Frameworks.md           # Documentação técnica das ferramentas utilizadas
├── Teste2/
│   ├── TransformacaoDados.py   # Extração de texto de PDFs (pdfplumber) e compressão (ZipFile)
│   └── Frameworks.md
├── Teste3/
│   ├── baixar_dados.py         # Scripts de extração automatizada de portais regulatórios (ANS)
│   ├── script_ans.py           # Modelagem e carga de dados estruturados
│   └── Frameworks.md
└── Teste4/
    ├── server.py               # API Backend desenvolvida em Python (Flask)
    ├── Relatorio_cadop.csv     # Base de dados estruturada utilizada pela API
    ├── Teste4 API.json         # Coleção do Postman para validação dos endpoints
    └── BuscaOperadoras/        # Interface Frontend SPA desenvolvida em Vue.js (Vite)
🛠️ Tecnologias e Frameworks
Backend & Engenharia de Dados
Python: Linguagem principal para scripts de automação e engenharia.  
MD

Pandas: Manipulação, limpeza e modelagem de grandes volumes de dados estruturados.  
MD

pdfplumber: Extração precisa de textos e tabelas complexas a partir de arquivos PDF.  
MD

ZipFile: Manipulação e compactação automatizada de pacotes de arquivos.  
MD

Flask: Framework leve para disponibilização dos endpoints da API REST.  
MD

Frontend
Vue.js 3: Framework progressivo para construção da interface de usuário.  
MD

Vite: Build tool rápida para otimização do ambiente de desenvolvimento Frontend.  
MD

⚙️ Detalhes de Implementation
1. Automação e Extração (Teste 1 & Teste 3)
Desenvolvimento de rotinas robustas de web scraping para download automatizado de relatórios e anexos técnicos a partir de portais governamentais/regulatórios.  
MD

Tratamento de exceções para lidar com instabilidades na rede e mudanças dinâmicas no DOM das páginas.  
MD

2. Processamento e Transformação (Teste 2)
Leitura automatizada de arquivos compactados e extração de dados tabulares não estruturados contidos em PDFs utilizando pdfplumber.  
MD

Pipeline de dados configurado no Pandas para limpar ruídos de formatação, converter tipos de dados e exportar o conteúdo final em formatos otimizados (como CSV).  
MD

3. Aplicação Full-Stack (Teste 4)
API REST (server.py): Consome a base estruturada Relatorio_cadop.csv e disponibiliza rotinas de busca, paginação e filtragem de operadoras de saúde por critérios específicos.  
MD

Frontend (BuscaOperadoras): Interface interativa que consome a API REST de forma assíncrona, exibindo dashboards e tabelas dinâmicas com recursos de busca reativa em tempo real.  
MD

🚀 Como Executar o Projeto
Pré-requisitos
Python 3.10 ou superior  
MD

Node.js (para o ecossistema Vue/Vite)  
MD

Configuração do Backend
Navegue até o diretório do servidor correspondente:

Bash
cd Teste4
Instale as dependências necessárias:

Bash
pip install -r requirements.txt
Inicie o servidor da API:

Bash
python server.py
Configuração do Frontend
Navegue até a pasta do projeto Vue:

Bash
cd Teste4/BuscaOperadoras
Instale os pacotes e dependências de desenvolvimento:

Bash
npm install
Inicie o servidor local de desenvolvimento:

Bash
npm run dev
