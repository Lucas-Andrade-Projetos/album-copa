# Passo 1 — Esqueleto Flask + "Hello World"

## O que foi feito

Criamos a base do projeto: um servidor web em Python que responde quando alguém acessa o site.

---

## Arquivos criados

### `requirements.txt`
Lista as bibliotecas externas que o projeto precisa. Funciona como uma "lista de compras" que o Python usa para instalar tudo de uma vez.

```
flask==3.1.1       → o framework web principal
flask-login==0.6.3 → vai gerenciar login de usuários (usado nos próximos passos)
werkzeug==3.1.3    → utilitários de segurança (hash de senha etc.)
```

**Por que fixar as versões?**
Se você escrever só `flask` sem versão, amanhã pode instalar uma versão diferente que quebra o código. Fixar garante que o projeto funcione igual em qualquer máquina.

---

### `.gitignore`
Diz ao Git quais arquivos NÃO devem ser versionados.

```
__pycache__/   → arquivos temporários que o Python gera automaticamente
*.pyc          → versão "compilada" do seu código Python (gerada automaticamente)
instance/      → onde fica o banco de dados (dados pessoais não vão pro GitHub)
.env           → arquivo com senhas e chaves secretas (NUNCA sobe pro GitHub)
venv/          → as bibliotecas instaladas (pesadas, cada um instala na própria máquina)
```

**Analogia:** É como dizer "não fotografe a nossa receita secreta nem os ingredientes frescos — só o livro de receitas vai para o arquivo público."

---

### `config.py`
Centraliza todas as configurações do projeto em um lugar só.

```python
SECRET_KEY     → chave usada para criptografar sessões de login
DATABASE       → caminho para o arquivo do banco de dados SQLite
PACKS_PER_DAY  → quantos pacotes o usuário pode abrir por dia (padrão: 5)
STICKERS_PER_PACK → quantas figurinhas por pacote (padrão: 5)
```

Essas configurações são lidas de **variáveis de ambiente** (`os.environ.get`). Se a variável não existir, usa um valor padrão. Isso é boa prática: em desenvolvimento usamos o padrão, em produção definimos valores reais sem alterar o código.

---

### `app/__init__.py` — o coração do Flask

```python
def create_app():
    ...
```

Esse padrão se chama **Application Factory** (fábrica de aplicação). Em vez de criar o app Flask diretamente no topo do arquivo, criamos uma *função* que monta o app e o retorna.

**Por que isso?**
- Facilita criar versões diferentes do app (produção, testes, desenvolvimento)
- Evita problemas de importação circular entre arquivos
- É o padrão oficial recomendado pelo Flask

A linha `app.config.from_pyfile("../config.py")` carrega as configurações do `config.py`.

A linha `os.makedirs(app.instance_path, exist_ok=True)` garante que a pasta `instance/` exista antes de qualquer acesso ao banco de dados.

---

### `run.py` — ponto de entrada

```python
from app import create_app
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
```

É o arquivo que você executa para ligar o servidor: `python run.py`.

`debug=True` faz o servidor:
- Recarregar automaticamente quando você salvar um arquivo (não precisa reiniciar)
- Mostrar erros detalhados no navegador (só use em desenvolvimento!)

---

### `README.md`
Documentação para qualquer pessoa que baixar o projeto saber como rodar. Inclui pré-requisitos, comandos de instalação e descrição da estrutura.

---

## Como testar

```bash
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar
venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Rodar
python run.py

# 5. Abrir no navegador
http://127.0.0.1:5000
# Deve aparecer: Hello, World Cup!
```

---

## Commit do GitHub

```bash
git init
git add -A
git commit -m "feat: initial Flask project skeleton"
git remote add origin https://github.com/SEU-USUARIO/album-copa.git
git push -u origin main
```

**O que significa `feat:`?**
É uma convenção chamada **Conventional Commits**. O prefixo indica o tipo de mudança:
- `feat:` → nova funcionalidade
- `fix:` → correção de bug
- `chore:` → tarefa de manutenção (configuração, dependências)
- `docs:` → apenas documentação

Isso torna o histórico de commits legível como um changelog automático.

---

## Estrutura do projeto após o Passo 1

```
Projeto/
├── app/
│   └── __init__.py     ← app Flask com rota "Hello World"
├── docs/
│   └── passo-01-explicacao.md
├── venv/               ← não vai pro Git
├── .gitignore
├── config.py
├── requirements.txt
├── README.md
└── run.py
```

---

## Conceitos aprendidos neste passo

| Conceito | O que é | Para que serve |
|----------|---------|----------------|
| Flask | Framework web Python | Criar sites e APIs com poucas linhas |
| Application Factory | Função que cria o app | Organização e testabilidade |
| Virtual Environment (venv) | Ambiente Python isolado | Não misturar dependências de projetos |
| requirements.txt | Lista de dependências | Reproduzir o ambiente em outra máquina |
| .gitignore | Lista de exclusões do Git | Não versionar arquivos desnecessários ou sensíveis |
| Conventional Commits | Padrão de mensagens Git | Histórico legível e semântico |

---

## Próximo passo

**Passo 2 — Banco de Dados e Seed:** criaremos as tabelas SQLite e inseriremos as 7 figurinhas iniciais.
