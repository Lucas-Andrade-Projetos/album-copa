# Passo 11 — Catálogo Dinâmico de Figurinhas

## O que foi feito

O admin agora pode adicionar novas figurinhas pelo painel, e elas aparecem automaticamente no álbum de todos os usuários e entram no sorteio de pacotes.

---

## Por que o álbum já era dinâmico?

Desde o Passo 4, o álbum busca todas as figurinhas direto do banco:

```python
# stickers.py
todas = db.execute(
    "SELECT id, number, player_name, country, rarity FROM stickers ORDER BY number"
).fetchall()
```

Não há nenhum `7` hardcoded. Se o banco tiver 100 figurinhas, o álbum mostra 100. Se tiver 8, mostra 8. O mesmo vale para `draw_stickers()` em `utils.py` — ele sempre busca `SELECT * FROM stickers` antes de sortear.

**Técnico:** O sistema é "data-driven" — o comportamento é determinado pelo estado do banco, não por constantes no código. Adicionar uma linha na tabela `stickers` é suficiente para mudar o comportamento de todas as features dependentes.

**Simples:** É como um cardápio de restaurante num quadro de giz. Você não precisa reimprimir o cardápio para mudar um prato — só apaga e escreve de novo. O banco de dados é o quadro de giz.

---

## Nova rota: `POST /admin/api/add-sticker`

```python
@bp.route("/api/add-sticker", methods=["POST"])
@login_required
@admin_required
def add_sticker():
    data        = request.get_json()
    player_name = (data.get("player_name") or "").strip()
    country     = (data.get("country") or "").strip()
    rarity      = data.get("rarity", "common")

    if not player_name or not country:
        return jsonify({"success": False, "error": "..."}), 400

    if rarity not in ("common", "rare", "legendary"):
        return jsonify({"success": False, "error": "Raridade inválida"}), 400

    db = get_db()
    row = db.execute("SELECT MAX(number) as max_n FROM stickers").fetchone()
    next_number = (row["max_n"] or 0) + 1

    db.execute(
        "INSERT INTO stickers (number, player_name, country, rarity) VALUES (?, ?, ?, ?)",
        (next_number, player_name, country, rarity),
    )
    db.commit()

    return jsonify({"success": True, "message": f"Figurinha #{next_number} ...", "reload": True})
```

### Validação de entrada

Toda rota que recebe dados externos deve validar antes de usar:

1. **Campos obrigatórios** — `player_name` e `country` não podem ser vazios
2. **Enum válido** — `rarity` só aceita os três valores conhecidos (`common`, `rare`, `legendary`). Aceitar qualquer string quebraria os pesos de sorteio e o CSS de raridade

O `.strip()` remove espaços em branco acidentais nas extremidades (ex: `"  Neymar  "` → `"Neymar"`).

### `MAX(number) + 1` para auto-numerar

```sql
SELECT MAX(number) as max_n FROM stickers
```

Busca o maior número já cadastrado. Se não houver nenhuma figurinha, `MAX()` retorna `NULL` — por isso o `or 0`:

```python
next_number = (row["max_n"] or 0) + 1
```

Com 7 figurinhas, retorna `8`. Sem nenhuma figurinha, retorna `1`. Simples e sem race condition para nosso caso de uso.

---

## Reload automático após adicionar

Quando adicionamos uma figurinha, os dropdowns de "Forçar Figurinha" e "Conceder Figurinha" precisam ser atualizados — eles foram gerados pelo Jinja2 no momento do carregamento da página.

A solução mais simples: recarregar a página após o sucesso.

```javascript
// Se a resposta trouxer reload: true, espera 1.2s e recarrega
if (d.reload) setTimeout(() => window.location.reload(), 1200);
```

O `setTimeout` de 1.2 segundos dá tempo de o usuário ler a mensagem de confirmação antes da página recarregar.

**Por que não atualizar o DOM dinamicamente?**

Seria possível adicionar a nova `<option>` nos três selects sem recarregar. Mas isso seria mais código para um resultado idêntico. Para ações raras (adicionar figurinha), simplicidade > otimização.

---

## Novo campo de texto no CSS

Os `<select>` já tinham estilo com `.admin-select`. Os novos `<input type="text">` precisavam do mesmo visual:

```css
.admin-select,
.admin-input {
    /* mesmos estilos de fundo escuro, borda, padding */
}

.admin-input::placeholder {
    color: var(--cor-texto-suave); /* cinza claro no placeholder */
}
```

Ao invés de duplicar as regras, agrupamos os dois seletores na mesma declaração — **DRY (Don't Repeat Yourself)**.

---

## Como testar

```bash
python run.py
```

1. Logue como admin e acesse `/admin/`
2. No card "Adicionar Nova Figurinha", preencha: nome `Cristiano Ronaldo`, país `Portugal`, raridade `Raro`
3. Clique em "Adicionar figurinha" — toast aparece, página recarrega após ~1 segundo
4. A figurinha #8 agora aparece nos dropdowns de Force/Grant
5. Acesse `/album` como qualquer usuário → álbum mostra 8 slots (o #8 aparece como `?` para quem ainda não tem)
6. Abra um pacote → `Cristiano Ronaldo` pode aparecer no sorteio!

---

## Próximo passo

**Passo 12 — Leaderboard (Capstone):** ranking de usuários por porcentagem de conclusão do álbum, com link no nav.
