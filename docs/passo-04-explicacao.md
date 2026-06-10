# Passo 4 — Visualização do Álbum (Estático)

## O que foi feito

O usuário agora vê seu álbum de figurinhas ao fazer login. O grid exibe todos os 7 slots: os que ele possui mostram nome e país do jogador, os que faltam aparecem como `?`. Uma barra de progresso mostra o percentual de conclusão.

---

## Como funciona (fluxo completo)

1. Usuário acessa `/album`
2. Flask verifica se está logado (`@login_required`)
3. Backend faz 2 queries no banco:
   - Busca todas as figurinhas do catálogo
   - Busca quais o usuário possui
4. Monta um dicionário de consulta rápida `{id: quantidade}`
5. Calcula progresso (`obtidas / total * 100`)
6. Envia tudo para o template Jinja2
7. Template renderiza o grid com os dados — sem JavaScript

---

## Arquivos modificados

### `app/stickers.py`

#### As duas queries
```python
# 1. Catálogo completo
todas = db.execute(
    "SELECT id, number, player_name, country, rarity FROM stickers ORDER BY number"
).fetchall()

# 2. O que o usuário tem
possuidas = db.execute(
    "SELECT sticker_id, quantity FROM user_stickers WHERE user_id = ?",
    (current_user.id,),
).fetchall()
```

#### O dicionário de lookup
```python
mapa_possuidas = {row["sticker_id"]: row["quantity"] for row in possuidas}
```

Isso se chama **dict comprehension** — uma forma compacta de criar um dicionário a partir de uma lista.

**Por que fazer isso em vez de verificar a lista a cada card?**

Imagina que o álbum tenha 640 figurinhas (como o álbum real). Para cada card, verificar uma lista de 500 figurinhas seria 640 × 500 = 320.000 comparações. Com o dicionário, são 640 comparações no total — uma por card. Isso é a diferença entre O(n²) e O(n) em ciência da computação.

---

### `app/templates/album.html`

#### Jinja2: `{% set %}`
```html
{% set qty = owned.get(sticker.id, 0) %}
```
Cria uma variável temporária dentro do template. `.get(chave, padrão)` retorna o valor do dicionário ou `0` se a chave não existir.

#### Classes CSS dinâmicas
```html
<div class="sticker-card {% if qty > 0 %}card-obtida rarity-{{ sticker.rarity }}{% else %}card-vazia{% endif %}">
```
O Jinja2 gera o HTML final já com as classes corretas antes de enviar ao navegador. Não há JavaScript envolvido nesse processo.

#### Filtro Jinja2 `| upper`
```html
{{ sticker.rarity | upper }}
```
Equivalente a `sticker.rarity.upper()` em Python. Jinja2 tem vários filtros nativos: `| lower`, `| capitalize`, `| length`, `| round`, etc.

---

### `app/static/css/style.css`

#### CSS Grid responsivo
```css
.sticker-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
}
```

- `display: grid` → ativa o CSS Grid (sistema de layout bidimensional)
- `auto-fill` → preenche a linha com quantas colunas couberem
- `minmax(140px, 1fr)` → cada coluna tem no mínimo 140px e no máximo 1 fração do espaço disponível
- Resultado: em telas grandes → 5-6 cards por linha. Em celular → 2-3 cards. **Sem uma linha de `@media query`.**

#### Position absolute dentro de relative
```css
.sticker-card   { position: relative; }
.sticker-number { position: absolute; top: 0.4rem; left: 0.6rem; }
.sticker-duplicata { position: absolute; top: 0.4rem; right: 0.6rem; }
```
O `absolute` posiciona em relação ao ancestral `relative` mais próximo. Isso permite colocar o `#1` no canto superior esquerdo e o `×3` no canto superior direito do card, independentemente do conteúdo central.

#### Brilho dourado no legendary
```css
.rarity-legendary {
    border-color: var(--cor-primaria);
    box-shadow: 0 0 10px rgba(245,166,35,0.3);
}
```
`box-shadow` com `rgba` de baixa opacidade cria o efeito de "brilho" sem ser agressivo.

---

## Como testar manualmente

```bash
python run.py
```

1. Faça login → veja 7 cards com `?`
2. Abra o banco com DB Browser e execute:
   ```sql
   INSERT INTO user_stickers (user_id, sticker_id, quantity) VALUES (1, 1, 1);
   INSERT INTO user_stickers (user_id, sticker_id, quantity) VALUES (1, 2, 3);
   ```
3. Recarregue `/album` → Mbappé aparece com borda dourada, Vinicius Jr com badge `×3`
4. Barra de progresso mostra `2 de 7 (28%)`

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| Server-side rendering | O servidor monta o HTML completo antes de enviar ao navegador |
| Dict comprehension | Criar dicionário de forma compacta a partir de lista |
| O(1) vs O(n) | Dicionário é busca instantânea; lista é busca linear |
| CSS Grid | Sistema de layout bidimensional nativo do CSS |
| `auto-fill` + `minmax` | Grid responsivo sem media queries |
| `position: absolute` | Posicionamento dentro de um container `relative` |
| Filtros Jinja2 | Transformações inline no template (`\| upper`, `\| length`...) |

---

## Próximo passo

**Passo 5 — Lógica de Abrir Pacote (Backend):** implementaremos o endpoint `POST /api/pack/open` que sorteia figurinhas com raridade ponderada, aplica o limite diário de 5 pacotes e registra no banco.
