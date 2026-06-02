# Passo 3 — Login e Registro de Usuário

## O que foi feito

Criamos as telas de login e cadastro. O usuário agora pode criar uma conta, entrar no site e manter a sessão entre páginas. Senhas são armazenadas com segurança usando hash.

---

## Conceito: como funciona o login em sites?

1. Usuário digita usuário e senha no formulário
2. O servidor verifica se o usuário existe no banco
3. Compara a senha digitada com o hash armazenado
4. Se correto, cria um **cookie de sessão** no navegador
5. Em cada página seguinte, o servidor lê esse cookie para saber quem está logado
6. Ao fazer logout, o cookie é destruído

**Analogia:** É como uma pulseira de festa — você recebe na entrada (login), mostra em cada atrativo (página protegida), e entrega na saída (logout).

---

## O que é hash de senha?

```
Senha original:  "minhasenha123"
Após hash:       "pbkdf2:sha256:260000$xK3...:9a2f8b..."
```

- O hash é **irreversível** — não tem como descobrir a senha original a partir do hash
- A função `generate_password_hash()` adiciona um **salt** aleatório — mesmo duas senhas iguais geram hashes diferentes
- A função `check_password_hash(hash, senha)` refaz o cálculo e compara — sem nunca "desencriptar" nada

**Por que não criptografar e depois descriptografar?** Porque se o banco de dados vazar, o atacante teria acesso a todas as senhas. Com hash, mesmo com o banco em mãos, as senhas são inacessíveis.

---

## Arquivos criados/modificados

### `app/auth.py` — rotas e lógica de autenticação

#### A classe `User`
```python
class User(UserMixin):
    def __init__(self, id, username, is_admin): ...
```
Flask-Login exige uma classe de usuário com 4 propriedades. `UserMixin` fornece os valores padrão — só precisamos adicionar nossos dados.

O método `User.get(user_id)` é chamado pelo Flask-Login a cada requisição para reconstruir o objeto do usuário a partir do ID guardado no cookie.

#### Blueprint
```python
bp = Blueprint("auth", __name__)
```
Um Blueprint é um "sub-aplicativo" que agrupa rotas relacionadas. Em vez de registrar todas as rotas no app principal, dividimos por funcionalidade (`auth`, `stickers`, `admin`). Facilita organização em projetos maiores.

#### Rota `POST /register`
Fluxo de validação em camadas:
1. Campo vazio?
2. Username muito curto (< 3 chars)?
3. Senha muito curta (< 6 chars)?
4. Senhas não coincidem?
5. Username já existe no banco?

Só chega no `INSERT` se nenhuma validação falhar.

#### Rota `POST /login`
```python
elif not check_password_hash(row["password"], password):
    error = "Senha incorreta."
```
Nota de segurança: a mensagem de erro não diz "senha incorreta para este usuário" — só "usuário não encontrado" ou "senha incorreta". Isso evita **user enumeration** (atacante descobre quais usuários existem pelo erro diferente).

#### `@login_required`
Decorador que intercepta a rota antes de executar. Se o usuário não estiver logado, redireciona para a página de login. Configuramos em `__init__.py`:
```python
login_manager.login_view = "auth.login"
```

---

### `app/stickers.py` — placeholder do álbum

Criado agora para não dar erro de rota inexistente quando o login redireciona para `/album`. Será completamente substituído no Passo 4.

---

### `app/__init__.py` — atualizado

```python
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
```

- `login_view` diz para onde redirecionar quem não está logado
- `user_loader` é o "tradutor" entre o ID no cookie e o objeto Python completo

```python
app.register_blueprint(auth.bp)
app.register_blueprint(stickers.bp)
```
Registra os Blueprints no app. Sem isso, as rotas não existem.

---

### Templates HTML com Jinja2

#### `base.html` — o molde
```html
{% block content %}{% endblock %}
```
Todo arquivo que usa `{% extends "base.html" %}` herda o layout (navbar, flash messages, CSS) e só precisa preencher o bloco `content`.

#### Jinja2: as duas sintaxes
| Sintaxe | Uso |
|---------|-----|
| `{{ variavel }}` | Exibir um valor |
| `{% if / for / block %}` | Lógica (condicionais, loops, blocos) |

#### Flash messages
```python
# No Python:
flash("Conta criada!", "success")

# No HTML:
{% for category, message in get_flashed_messages(with_categories=true) %}
    <div class="flash flash-{{ category }}">{{ message }}</div>
{% endfor %}
```
As mensagens são armazenadas na sessão e consumidas uma única vez — na próxima requisição não aparecem mais.

---

### `app/static/css/style.css`

Usa **CSS custom properties** (variáveis):
```css
:root {
    --cor-primaria: #f5a623;
}
.btn-primary { background-color: var(--cor-primaria); }
```
Alterar `--cor-primaria` uma vez muda a cor em todo o site. Muito mais fácil que buscar e substituir.

---

## Correção que fizemos

Os arquivos `templates/` e `static/` foram criados na raiz do projeto, mas o Flask procura em `app/templates/` e `app/static/` porque `Flask(__name__)` é chamado dentro do pacote `app/`.

**Regra geral:** templates e estáticos ficam dentro do pacote Flask — ao lado do `__init__.py`.

---

## Como testar manualmente

```bash
python run.py
# Acesse http://127.0.0.1:5000
```

1. Acesse `/register` → crie uma conta
2. Você deve ser redirecionado para `/login` com mensagem "Conta criada!"
3. Faça login → redirecionado para `/album`
4. Tente acessar `/album` sem estar logado → redirecionado para `/login`
5. Clique em "Sair" → redirecionado para `/login`
6. Tente registrar o mesmo usuário → mensagem "O usuário 'X' já existe."

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| Hash de senha | Transformação irreversível — nunca armazenar senha pura |
| Flask-Login | Biblioteca que gerencia sessões de usuário |
| Blueprint | Agrupamento de rotas por funcionalidade |
| Cookie de sessão | "Crachá" criptografado no navegador |
| `@login_required` | Decorator que bloqueia rotas para não logados |
| Jinja2 | Linguagem de templates do Flask |
| Flash messages | Mensagens temporárias entre requisições |
| User enumeration | Vulnerabilidade: revelar quais usuários existem pelo erro |

---

## Próximo passo

**Passo 4 — Visualização do Álbum:** o usuário verá o grid das 7 figurinhas. Slots que ainda não possui aparecem como `?`. Barra de progresso mostra quantas já tem.
