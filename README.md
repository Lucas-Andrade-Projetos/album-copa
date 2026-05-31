# Álbum de Figurinhas da Copa do Mundo

Site de álbum de figurinhas com abertura de pacotes diários, sistema de login e painel admin.

## Pré-requisitos

- Python 3.11+
- pip

## Como rodar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. (A partir do Passo 2) Inicializar o banco de dados
flask --app run init-db

# 4. Rodar o servidor
python run.py
```

Acesse: http://127.0.0.1:5000

## Variáveis de Ambiente (opcional)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `FLASK_SECRET_KEY` | `dev-secret-troque-em-producao` | Chave de sessão — troque em produção |
| `PACKS_PER_DAY` | `5` | Pacotes que cada usuário pode abrir por dia |
| `STICKERS_PER_PACK` | `5` | Figurinhas por pacote |

## Estrutura do Projeto

```
app/            → código Python (rotas, banco, lógica)
static/         → CSS e JavaScript do frontend
templates/      → páginas HTML (Jinja2)
instance/       → banco de dados SQLite (não versionado)
schema.sql      → estrutura das tabelas
config.py       → configurações
run.py          → ponto de entrada
```
