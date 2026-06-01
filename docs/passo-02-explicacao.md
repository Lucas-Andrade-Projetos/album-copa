# Passo 2 — Banco de Dados SQLite e Seed

## O que foi feito

Criamos a estrutura do banco de dados e inserimos as 7 figurinhas iniciais do álbum.

---

## O que é SQLite?

SQLite é um banco de dados que vive em um único arquivo `.db` no seu computador. Diferente de bancos como PostgreSQL ou MySQL, não precisa de um servidor rodando separado — o Python abre o arquivo diretamente.

**Analogia:** Pensa no banco como uma planilha Excel com várias abas. Cada aba é uma tabela. As abas se "conversam" através de IDs.

---

## Arquivos criados/modificados

### `schema.sql` — a planta das tabelas

Define quais tabelas existem e quais colunas cada uma tem. Não guarda dados, só estrutura.

#### Tabela `users`
```sql
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único, gerado automaticamente
    username    TEXT    NOT NULL UNIQUE,             -- nome único, obrigatório
    password    TEXT    NOT NULL,                    -- senha (armazenada como hash)
    is_admin    INTEGER NOT NULL DEFAULT 0,          -- 0 = usuário comum, 1 = admin
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))  -- data de criação automática
);
```

#### Tabela `stickers` — o catálogo
```sql
CREATE TABLE IF NOT EXISTS stickers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    number      INTEGER NOT NULL UNIQUE,   -- número da figurinha no álbum
    player_name TEXT    NOT NULL,
    country     TEXT    NOT NULL,
    rarity      TEXT    NOT NULL DEFAULT 'common'  -- common | rare | legendary
);
```

#### Tabela `user_stickers` — o álbum de cada usuário
```sql
CREATE TABLE IF NOT EXISTS user_stickers (
    ...
    UNIQUE(user_id, sticker_id)  -- cada figurinha aparece 1 vez; duplicata vira +1 na quantity
);
```

**Conceito importante — chave estrangeira (`REFERENCES`):** A coluna `user_id` referencia a tabela `users`. Se você tentar inserir um `user_sticker` com um `user_id` que não existe, o banco rejeita. Isso garante que os dados sejam consistentes.

#### Tabela `pack_openings` — histórico de pacotes
Cada vez que alguém abre um pacote, gravamos um registro aqui. Usamos isso para contar quantos pacotes o usuário já abriu hoje.

#### Tabela `admin_overrides` — fila de figurinhas forçadas
Quando o admin quer garantir que o usuário receba uma figurinha específica no próximo pacote, insere aqui. O sistema consome esse registro na hora de sortear.

---

### `app/database.py` — o gerenciador do banco

#### `get_db()` — abre a conexão
```python
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(...)
```
- `g` é o objeto "mochila da requisição" do Flask. Vive enquanto o Flask está processando uma página e é descartado depois.
- A conexão é aberta uma vez por requisição, não uma vez por chamada. Eficiente.
- `row_factory = sqlite3.Row` permite acessar colunas pelo nome: `row["username"]` em vez de `row[0]`.

#### `close_db()` — fecha a conexão
Registrada como hook de teardown — o Flask chama automaticamente no final de cada requisição.

#### `init_db()` — cria as tabelas
Lê o `schema.sql` e executa todos os `CREATE TABLE IF NOT EXISTS`.

#### `seed_stickers()` — insere as figurinhas
```python
db.executemany(
    "INSERT OR IGNORE INTO stickers (number, player_name, country, rarity) VALUES (?, ?, ?, ?)",
    stickers,
)
```
- `executemany` executa a mesma query para cada linha da lista — eficiente.
- `INSERT OR IGNORE` pula silenciosamente se a figurinha já existe. Seguro rodar várias vezes.
- `?` são **placeholders parametrizados** — NUNCA use f-strings ou concatenação de strings em queries SQL. Isso abre brecha para SQL Injection (um atacante pode apagar seu banco inteiro com um input malicioso).

#### O que é SQL Injection?
```python
# ERRADO (vulnerável):
db.execute(f"SELECT * FROM users WHERE username = '{username}'")
# Se username = "'; DROP TABLE users; --", o banco executa o DROP TABLE!

# CORRETO (seguro):
db.execute("SELECT * FROM users WHERE username = ?", (username,))
# O ? é tratado como dado puro, nunca como código SQL.
```

#### `init_db_command()` — o comando de terminal
```python
@click.command("init-db")
def init_db_command():
    ...
```
Registra o comando `flask init-db` no CLI do Flask.

#### `init_app(app)` — registra no Flask
```python
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
```
Chamada dentro de `create_app()` para conectar as funções ao ciclo de vida do Flask.

---

### `app/__init__.py` — atualizado

```python
from . import database
database.init_app(app)
```

`from . import database` é uma importação relativa — o `.` significa "do mesmo pacote (`app/`)". É preferível à importação absoluta dentro do pacote para evitar ambiguidade.

---

## Como testar manualmente

```bash
# Ativar o ambiente virtual
venv\Scripts\activate

# Inicializar o banco
flask --app run init-db
# Saída esperada: "Banco de dados inicializado com 7 figurinhas."

# Verificar o banco (opcional — requer DB Browser for SQLite)
# Abrir: instance/album.db
# Verificar tabelas e 7 linhas em stickers
```

---

## Commit realizado

```
feat: SQLite schema and seed data
```

**Arquivos incluídos:**
- `schema.sql` (novo)
- `app/database.py` (novo)
- `app/__init__.py` (modificado — adicionou `database.init_app(app)`)

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| SQLite | Banco de dados em arquivo, sem servidor |
| Schema | Estrutura das tabelas (colunas, tipos, restrições) |
| Chave primária | ID único de cada linha |
| Chave estrangeira | Referência a outra tabela — garante consistência |
| SQL parametrizado | `?` em vez de f-string — protege contra SQL Injection |
| `g` do Flask | Objeto temporário por requisição |
| Seed | Dados iniciais inseridos na primeira execução |

---

## Próximo passo

**Passo 3 — Login e Registro:** o usuário poderá criar uma conta e fazer login. Vamos usar Flask-Login para gerenciar sessões e Werkzeug para fazer hash das senhas.
