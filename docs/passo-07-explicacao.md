# Passo 7 — Painel Admin

## O que foi feito

Criamos uma área de controle protegida acessível só por usuários com `is_admin = 1`. O admin pode forçar figurinhas em pacotes, conceder diretamente, zerar limites diários, limpar álbuns e visualizar o progresso de todos os usuários.

---

## Como funciona a proteção de rota

```python
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

**Técnico:** Decorator personalizado usando `functools.wraps`. `@wraps(f)` copia os metadados da função original (nome, docstring) para a função `decorated` — sem isso, o Flask veria todas as rotas com o mesmo nome `decorated` e lançaria um erro de endpoint duplicado.

**Simples:** É um "filtro" que toda rota admin passa antes de executar. Se o usuário não for admin, a porta fecha com 403 ("Proibido"). `@wraps` é como colocar a plaquinha do quarto correto na porta — sem ela, todas as portas pareceriam iguais para o sistema.

---

## O decorator duplo nas rotas

```python
@bp.route("/")
@login_required
@admin_required
def index():
    ...
```

Os decorators são aplicados de baixo para cima. Primeiro `@admin_required` (que já verifica se está autenticado), depois `@login_required` (que redireciona para login se não estiver). A ordem garante a mensagem certa: não autenticado → redireciona para login; autenticado mas não admin → 403.

---

## A lógica de `admin_overrides` em `utils.py`

```python
def draw_stickers(db, n, user_id=None):
    # 1. Consome overrides pendentes primeiro
    forcadas = []
    if user_id is not None:
        overrides = db.execute(
            "SELECT ... FROM admin_overrides WHERE used = 0 LIMIT ?", (n,)
        ).fetchall()
        for row in overrides:
            forcadas.append({...})
            db.execute("UPDATE admin_overrides SET used = 1 WHERE id = ?", (row["id"],))

    # 2. Preenche o restante com sorteio normal
    slots_restantes = n - len(forcadas)
    aleatorias = random.choices(..., k=slots_restantes)

    return forcadas + aleatorias
```

**Técnico:** O override é consumido atomicamente — buscamos e marcamos como `used = 1` na mesma chamada, dentro da mesma conexão. Isso evita race conditions (dois pacotes abrindo ao mesmo tempo e consumindo o mesmo override).

**Simples:** A figurinha forçada "entra na fila" e sai quando o próximo pacote é aberto. Depois de sair, a fila marca ela como "já usada" para não sair duas vezes.

---

## As rotas do admin

### `POST /admin/api/force-sticker`
Insere na tabela `admin_overrides` com `used = 0`. Na próxima vez que o usuário abrir um pacote, essa figurinha será garantida.

### `POST /admin/api/grant-sticker`
Upsert direto em `user_stickers` — mesma lógica do `award_stickers`. A diferença é que não passa pelo fluxo de pacote: não conta no limite diário, não registra em `pack_openings`.

### `POST /admin/api/reset-daily`
```sql
DELETE FROM pack_openings WHERE user_id = ? AND date(opened_at) = date('now')
```
Simplesmente apaga os registros de hoje — o contador zera porque a contagem é feita ao vivo por query.

### `POST /admin/api/clear-album`
```sql
DELETE FROM user_stickers WHERE user_id = ?
```
Remove todas as figurinhas do usuário. Usado para testar o fluxo completo do zero.

---

## O template `admin.html`

### JavaScript inline (por que está no template?)
O JavaScript do admin é simples e específico para essa página. Colocar em arquivo separado seria excessivo para 30 linhas. A regra: JS pequeno e específico pode ficar inline; JS reutilizável ou grande vai em arquivo `.js`.

### Função `acao(url, body)`
```javascript
async function acao(url, body) {
    const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type: application/json" },
        body: JSON.stringify(body),
    });
    const d = await r.json();
    // exibe feedback...
}
```
Uma função genérica que todas as ações do admin reutilizam. Evita repetição — os 4 botões chamam a mesma função com URLs e dados diferentes.

### Feedback toast
```javascript
fb.style.display = "block";
```
O feedback aparece no canto inferior direito como uma notificação flutuante (`position: fixed`). Não recarrega a página — tudo acontece via `fetch` e DOM.

### `confirm()` antes de limpar o álbum
```javascript
if (confirm(`Limpar TODO o álbum de "${nome}"?`)) {
    acao(...)
}
```
`confirm()` é uma caixa de diálogo nativa do navegador que exige confirmação antes de ações destrutivas. Simples e eficaz para um painel interno.

---

## Criar usuário admin

Não há tela de cadastro admin (por segurança). O admin é criado diretamente no banco:

```python
# Via script Python
conn.execute(
    "UPDATE users SET is_admin = 1 WHERE username = ?", ("seu_usuario",)
)
```

Ou via DB Browser for SQLite:
```sql
UPDATE users SET is_admin = 1 WHERE username = 'seu_usuario';
```

---

## Como testar

```bash
python run.py
```

1. Faça login como `admin` / `admin123`
2. O link **"Admin"** aparece na navbar (só para admins)
3. Acesse `/admin` → painel com os 4 cards de ação
4. **Forçar figurinha:** escolha um usuário e uma figurinha → clique → faça login como esse usuário → abra um pacote → a figurinha aparece garantida
5. **Conceder direto:** adiciona ao álbum instantaneamente
6. **Resetar limite:** o usuário pode abrir 5 pacotes novamente hoje
7. **Limpar álbum:** remove tudo (pede confirmação antes)
8. Tente acessar `/admin` como usuário comum → 403

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| Decorator personalizado | Função que "embrulha" outra adicionando comportamento |
| `@functools.wraps` | Preserva metadados da função original ao decorar |
| `abort(403)` | Lança exceção HTTP sem retorno explícito |
| Admin override | Injeção garantida de item no próximo evento aleatório |
| Race condition | Dois processos competindo pelo mesmo recurso simultaneamente |
| `confirm()` | Diálogo de confirmação nativo do navegador |
| Toast notification | Feedback flutuante sem recarregar a página |

---

## Próximo passo

**Passo 8 — Progresso e Conclusão do Álbum:** barra de progresso dinâmica via JavaScript, overlay de parabéns quando o álbum estiver 100% completo, e badge de duplicatas com contagem.
