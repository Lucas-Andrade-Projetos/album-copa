# Passo 10 — Configuração e Segurança

## O que foi feito

O projeto agora carrega segredos de um arquivo `.env`, avisa quando a chave secreta padrão está em uso, e protege o cookie de sessão contra dois tipos de ataque comuns.

---

## Variáveis de ambiente

### O que é uma variável de ambiente?

**Técnico:** São pares `CHAVE=VALOR` definidos no sistema operacional (ou em um arquivo `.env`) que um processo pode ler em tempo de execução. Permitem separar configuração do código — o mesmo binário se comporta diferente no desenvolvimento e em produção sem uma única linha de código mudada.

**Simples:** É como o "modo turbo" de um videogame. O jogo vem com o modo normal ativado, mas você pode colocar um código especial para ligar o modo turbo. O arquivo `.env` é onde você guarda esses códigos especiais, sem precisar abrir o código do jogo.

### Por que não colocar a chave secreta diretamente no código?

```python
# ERRADO — nunca faça isso
SECRET_KEY = "minha-chave-ultra-secreta-123"
```

Se você fizer `git push`, a chave vai parar no GitHub — pública para o mundo. Qualquer pessoa que vir o repositório pode forjar cookies de sessão e fazer login como qualquer usuário.

```python
# CORRETO — lê do ambiente, com fallback para desenvolvimento
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-troque-em-producao")
```

Em produção, você define `FLASK_SECRET_KEY` no servidor. No git vai só o código, não o segredo.

---

## python-dotenv

Instalamos `python-dotenv` para que o arquivo `.env` seja lido automaticamente quando o servidor inicia.

```python
# run.py
from dotenv import load_dotenv
load_dotenv()          # lê o .env e injeta as variáveis no os.environ

from app import create_app
app = create_app()
```

O `load_dotenv()` precisa ser chamado **antes** de qualquer import do Flask, porque o `config.py` lê as variáveis de ambiente no momento em que é importado.

### Arquivo `.env.example`

Criamos `.env.example` — um template público que mostra quais variáveis o projeto aceita, sem os valores reais:

```
FLASK_SECRET_KEY=troque-por-uma-chave-aleatoria-longa
PACKS_PER_DAY=5
STICKERS_PER_PACK=5
```

O fluxo para um novo desenvolvedor é:
1. Clonar o repo
2. Copiar: `cp .env.example .env`
3. Gerar uma chave: `python -c "import secrets; print(secrets.token_hex(32))"`
4. Colar no `.env`

O `.env` já está no `.gitignore` desde o Passo 1, então nunca vai ao GitHub.

---

## Aviso de segurança no startup

```python
_DEV_SECRET = "dev-secret-troque-em-producao"

if app.config["SECRET_KEY"] == _DEV_SECRET:
    warnings.warn(
        "FLASK_SECRET_KEY está com o valor padrão inseguro. ...",
        stacklevel=2,
    )
```

Quando o servidor inicia sem um `.env` real, aparece no terminal:

```
UserWarning: FLASK_SECRET_KEY está com o valor padrão inseguro.
```

Isso não impede o servidor de funcionar (útil para desenvolvimento) mas lembra o desenvolvedor de configurar o segredo antes de publicar.

---

## Segurança do cookie de sessão

### `SESSION_COOKIE_HTTPONLY = True`

**Técnico:** Instrui o navegador a **não** expor o cookie para JavaScript via `document.cookie`. Só o navegador mesmo tem acesso, e só o envia em requisições HTTP.

**Simples:** Imagina que o cookie de sessão é uma chave de cofre. Com `HttpOnly`, você pode usar a chave para abrir o cofre, mas não pode pegá-la com as mãos e copiá-la. Isso protege contra ataques XSS — se um código malicioso aparecer na página, ele não consegue roubar a chave.

### `SESSION_COOKIE_SAMESITE = "Lax"`

**Técnico:** Instrui o navegador a **não** enviar o cookie em requisições cross-site iniciadas por terceiros. O modo `Lax` ainda permite navegação normal (clique em link), mas bloqueia submissões automáticas de formulários de outros domínios — a principal técnica de CSRF.

**Simples:** Imagina que você está logado no site do banco. Se alguém criar um site falso e colocar um formulário que envia dinheiro para eles, normalmente o navegador mandaria seu cookie de sessão junto — mesmo sem você saber. `SameSite=Lax` faz o navegador dizer "esse pedido veio de outro site, não vou incluir o cookie".

---

## Auditoria SQL — resultado

Verificamos todos os arquivos do projeto:

| Arquivo | Queries | F-strings em SQL? |
|---------|---------|-------------------|
| `auth.py` | 3 queries | Nenhuma ✓ |
| `stickers.py` | 5 queries | Nenhuma ✓ |
| `utils.py` | 5 queries | Nenhuma ✓ |
| `admin.py` | 10 queries | Nenhuma ✓ |
| `database.py` | `executemany` | Nenhuma ✓ |

Todas as queries usam `?` como placeholder. Os f-strings que existem em `admin.py` são apenas para montar as **mensagens de resposta JSON** — nunca dentro do SQL.

**Por que f-string em SQL é perigoso?**

```python
# VULNERÁVEL — SQL Injection
query = f"SELECT * FROM users WHERE username = '{username}'"

# SEGURO — parameterizado
query = "SELECT * FROM users WHERE username = ?"
db.execute(query, (username,))
```

Se `username` for `' OR '1'='1`, a primeira versão vira:
```sql
SELECT * FROM users WHERE username = '' OR '1'='1'
```
...que retorna TODOS os usuários. Com `?`, o driver trata o valor como dado, não como código SQL.

---

## Como testar

```bash
python run.py
```

**Sem `.env`:** o terminal mostra o aviso de chave insegura — app funciona normalmente (desenvolvimento).

**Com `.env`:**
```
FLASK_SECRET_KEY=abc123def456...
```
O aviso desaparece. Se você mudar a chave, todas as sessões ativas são invalidadas (usuários precisam logar de novo) — comportamento correto em rotação de segredos.

---

## Próximo passo

**Passo 11 — Catálogo Dinâmico:** o admin pode adicionar novas figurinhas pelo painel, e o álbum de todos os usuários expande automaticamente.
