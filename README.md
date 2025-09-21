# Sistema de Gestão de Pesquisa (SGP)

Bem-vindo ao Sistema de Gestão de Pesquisa (SGP), um projeto desenvolvido em Django e Django Templates para facilitar a criação e o gerenciamento de pesquisas (surveys). Este README fornece informações essenciais sobre como configurar e executar o projeto em seu ambiente local.

## Requisitos

Certifique-se de que você tenha os seguintes requisitos instalados em seu sistema:

- Python (versão recomendada: 3.7 ou superior)
- Django (instalado automaticamente ao seguir as instruções abaixo)
- Outras dependências listadas no arquivo `requirements.txt`


## Instalação das Dependências

Com o ambiente virtual ativado, instale as dependências do projeto usando o comando:
```bash
pip install -r requirements.txt
```


## Rodar o projeto

Após instalar as dependências, aplique as migrations no banco de dados com o comando:
```bash
python manage.py migrate
```

Agora o projeto jã pode ser inicializado com o comando:
```bash
python manage.py runserver
```

Após isso, o sistema estará pronto para ser acessado em:
[http://localhost:8000](http://localhost:8000)

## Variáveis de ambiente

1. Copie o arquivo de exemplo e ajuste conforme necessário:
```bash
cp .env.example .env
```

## Documentação da API

- Esquema OpenAPI: `/api/schema/`
- Swagger UI: `/api/docs/`
- Redoc: `/api/redoc/`
