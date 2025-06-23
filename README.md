# MovieBot - Recomendador Inteligente de Filmes

MovieBot é uma aplicação Flask que utiliza um Large Language Model (LLM) para fornecer recomendações personalizadas de filmes com base nas preferências do utilizador.

## Funcionalidades

*   Recomendações de filmes baseadas em linguagem natural.
*   Seleção de "tipo de utilizador" (Casual, Crítico, Entusiasta) para refinar as recomendações.
*   Interface web simples e intuitiva.
*   Base de dados de filmes carregada a partir de um arquivo CSV.
*   Suporte para múltiplos provedores de LLM (OpenAI, Groq - configurável via variáveis de ambiente).

## Pré-requisitos

*   Python 3.8 ou superior
*   Pip (gerenciador de pacotes Python)
*   Git (para clonar o repositório)
*   Uma chave de API de um provedor de LLM suportado (ex: Groq).

## Configuração e Instalação

Siga estes passos para configurar e executar o MovieBot localmente:

1.  **Clone o Repositório:**
    Abra o seu terminal e clone o projeto do GitHub:
    ```bash
    git clone https://github.com/SEU_NOME_DE_USUARIO/NOME_DO_SEU_REPOSITORIO.git
    cd NOME_DO_SEU_REPOSITORIO
    ```
    *(Substitua `SEU_NOME_DE_USUARIO/NOME_DO_SEU_REPOSITORIO` pelo URL real do seu projeto no GitHub)*

2.  **Crie e Ative um Ambiente Virtual (Recomendado):**
    É uma boa prática usar ambientes virtuais para isolar as dependências do projeto.
    ```bash
    python -m venv venv
    ```
    Para ativar o ambiente virtual:
    *   No Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   No macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Instale as Dependências:**
    Com o ambiente virtual ativado, instale as bibliotecas Python necessárias:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as Variáveis de Ambiente:**
    O MovieBot precisa de chaves de API para se conectar aos serviços de LLM.
    *   Copie o arquivo de exemplo `.env.example` para um novo arquivo chamado `.env`:
        ```bash
        # No Windows (usando PowerShell ou cmd)
        copy .env.example .env

        # No macOS/Linux
        cp .env.example .env
        ```
    *   Abra o arquivo `.env` num editor de texto e preencha as informações necessárias:
        ```plaintext
        # LLM API Configuration
        # Escolha o seu provedor de LLM: "openai", "groq"
        LLM_PROVIDER=groq

        # Preencha APENAS a chave de API para o LLM_PROVIDER escolhido.
        OPENAI_API_KEY=SUA_CHAVE_OPENAI_AQUI_SE_USAR_OPENAI
        GROQ_API_KEY=SUA_CHAVE_GROQ_AQUI_SE_USAR_GROQ
        TOGETHER_API_KEY= # Deixe em branco se não usar

        # Flask Configuration (geralmente não precisa mudar para desenvolvimento local)
        FLASK_APP=app.py
        FLASK_ENV=development
        FLASK_DEBUG=True
        ```
        **Importante:** Obtenha sua chave de API do provedor LLM escolhido (ex: [Groq Console](https://console.groq.com/keys) para a Groq API). O arquivo `.env` NUNCA deve ser comitado para o Git.

5.  **Popule a Base de Dados de Filmes (Se necessário):**
    O arquivo `movies.csv` já deve estar incluído no repositório com uma lista de filmes. Se por algum motivo ele não existir ou estiver vazio, você pode (re)criá-lo executando o script `populate_movies.py`:
    ```bash
    python populate_movies.py
    ```
    Isso irá gerar o arquivo `movies.csv`.

## Como Executar

Após a configuração e instalação, inicie a aplicação Flask:

```bash
flask run
```
Ou, alternativamente:
```bash
python app.py
```

Abra o seu navegador e acesse: `http://127.0.0.1:5000`

Você deverá ver a interface do MovieBot pronta para receber suas perguntas!

## Estrutura do Projeto

```
.
├── app.py                # Lógica principal da aplicação Flask e LLM
├── populate_movies.py    # Script para gerar o movies.csv
├── movies.csv            # Base de dados de filmes
├── requirements.txt      # Dependências Python
├── templates/
│   └── index.html        # Template HTML da interface
├── .env                  # Exemplo de arquivo de variáveis de ambiente
├── .gitignore            # Arquivos e pastas ignorados pelo Git
└── README.md             # Este arquivo
```

## Contribuições

Contribuições são bem-vindas! Se encontrar bugs ou tiver sugestões, por favor, abra uma "issue" no GitHub.

## Licença

Este projeto é para fins educacionais. Por favor, verifique as licenças das dependências e dos modelos LLM utilizados se for usar comercialmente.
