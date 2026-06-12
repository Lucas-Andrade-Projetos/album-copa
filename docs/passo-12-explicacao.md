# Passo 12 — Leaderboard (Capstone)

## O que foi feito

O site agora tem um ranking de todos os usuários, ordenado por porcentagem de conclusão do álbum. Cada usuário é destacado em sua própria linha, com medalhas para o top 3 e badge "Completo!" para quem terminou o álbum.

---

## A query SQL do ranking

```sql
SELECT u.id, u.username, COUNT(us.sticker_id) as obtidas
FROM users u
LEFT JOIN user_stickers us ON us.user_id = u.id
GROUP BY u.id
ORDER BY obtidas DESC, u.username ASC
```

### Dissecando cada parte

**`LEFT JOIN`** — Inclui usuários que ainda não têm NENHUMA figurinha. Um `INNER JOIN` excluiria esses usuários do ranking — eles simplesmente não apareceriam. Com `LEFT`, todos os usuários aparecem, e quem não tem figurinha recebe `COUNT = 0`.

**`COUNT(us.sticker_id)`** — Conta quantas linhas de `user_stickers` existem para aquele usuário. Diferente de `COUNT(*)`, se o JOIN não encontrou nenhuma linha (usuário sem figurinhas), conta 0 em vez de 1.

**`GROUP BY u.id`** — Agrupa as linhas por usuário para que o `COUNT` seja calculado por pessoa.

**`ORDER BY obtidas DESC, u.username ASC`** — Ordena por mais figurinhas primeiro. Em caso de empate no número de figurinhas, ordena alfabeticamente pelo nome. Isso garante um ranking estável e determinístico.

**Técnico:** É um padrão clássico de SQL analítico — `SELECT ... FROM entidade LEFT JOIN detalhe GROUP BY entidade.id ORDER BY agregação`. Sem ORM, você vê exatamente o que o banco executa.

**Simples:** Imagina uma tabela de escola com aluno e matéria. `GROUP BY aluno` + `COUNT(matéria)` conta quantas matérias cada aluno fez. `ORDER BY` coloca na ordem de quem fez mais.

---

## O total de figurinhas

```python
total = db.execute("SELECT COUNT(*) as n FROM stickers").fetchone()["n"]
```

Buscamos o total separadamente (uma query) em vez de colocar dentro da query de ranking. Isso é mais limpo — o total é o mesmo para todos os usuários, não faz sentido recalcular por usuário.

O `percent` é calculado em Python para cada usuário:
```python
percent = round((row["obtidas"] / total) * 100) if total > 0 else 0
```

O `if total > 0` evita divisão por zero se o banco ainda não tiver figurinhas.

---

## O campo `eu`

```python
"eu": row["id"] == current_user.id,
```

Marcamos qual linha pertence ao usuário logado. No template, isso aplica uma classe CSS especial:

```html
<tr class="{{ 'leaderboard-eu' if r.eu }}">
```

```css
.leaderboard-eu td {
    background-color: rgba(245, 166, 35, 0.07); /* fundo dourado suave */
}
```

Isso ajuda o usuário a se encontrar rapidamente no ranking, mesmo que esteja em posição baixa.

---

## Medalhas com Jinja2

```jinja2
{% if r.pos == 1 %}🥇
{% elif r.pos == 2 %}🥈
{% elif r.pos == 3 %}🥉
{% else %}{{ r.pos }}
{% endif %}
```

Para as 3 primeiras posições, mostramos um emoji de medalha. Para as demais, o número da posição. Simples e visual.

---

## Badges

Dois badges aparecem condicionalmente:

```html
{% if r.eu %}<span class="badge-eu">você</span>{% endif %}
{% if r.percent == 100 %}<span class="badge-completo">Completo!</span>{% endif %}
```

- `badge-eu`: fundo dourado, texto preto — identifica o usuário atual
- `badge-completo`: fundo verde — celebra quem terminou o álbum

---

## CSS da tabela

A tabela usa a mesma abordagem da tabela do painel admin, mas com algumas adições:

```css
.lb-progress-bar {
    flex: 1;              /* ocupa todo o espaço disponível */
    height: 8px;
    background-color: var(--cor-borda);
    border-radius: 999px; /* bordas totalmente arredondadas */
    overflow: hidden;
}

.lb-progress-fill {
    height: 100%;
    background-color: var(--cor-primaria);
    transition: width 0.4s ease; /* animação suave ao carregar */
}
```

O `transition` faz a barra de progresso "crescer" com uma animação suave quando a página carrega — um detalhe que melhora a percepção de qualidade.

Em mobile (`max-width: 600px`), o percentual textual some (`display: none`) para economizar espaço — a barra visual ainda aparece.

---

## Link no navbar

```html
<a href="{{ url_for('stickers.leaderboard') }}">Ranking</a>
```

Adicionado entre "Abrir Pacote" e "Admin" (quando aplicável). Visível para todos os usuários logados.

---

## Como testar

```bash
python run.py
```

1. Crie 2–3 usuários diferentes
2. Abra pacotes com cada usuário para ter quantidades diferentes de figurinhas
3. Acesse `/leaderboard` → ranking em ordem decrescente de figurinhas
4. Sua linha aparece com fundo dourado e badge "você"
5. Use o painel admin para conceder todas as figurinhas a um usuário → badge "Completo!" aparece na linha dele

---

## Resumo do Projeto Completo

| Passo | Feature | Principais conceitos |
|-------|---------|---------------------|
| 1 | Esqueleto Flask | Application Factory, Blueprints |
| 2 | Banco de Dados | SQLite, schema.sql, seed |
| 3 | Login/Registro | Flask-Login, Werkzeug hash, sessão |
| 4 | Álbum Estático | Jinja2, CSS Grid, dict comprehension |
| 5 | Lógica de Pacotes | random.choices, pesos de raridade, limite diário |
| 6 | UI de Pacotes | fetch + async/await, CSS flip 3D |
| 7 | Painel Admin | admin_required decorator, admin_overrides |
| 8 | Progresso | API JSON, barra de progresso, overlay |
| 9 | UX Polish | errorhandler, spinner, responsividade |
| 10 | Segurança | dotenv, warnings, cookie HttpOnly/SameSite |
| 11 | Catálogo Dinâmico | data-driven design, validação de entrada |
| 12 | Leaderboard | LEFT JOIN + GROUP BY, ranking SQL |

O projeto começou com um "Hello World" em um arquivo só e terminou com 12 features funcionais, banco de dados relacional, autenticação, painel admin, e interface completa — tudo com Python, SQL e JavaScript puros, sem frameworks de front-end.
