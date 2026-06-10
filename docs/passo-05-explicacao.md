# Passo 5 — Lógica de Abrir Pacote (Backend)

## O que foi feito

Implementamos a mecânica principal do jogo: abrir pacotes de figurinhas. O backend sorteia figurinhas com probabilidades diferentes por raridade, aplica limite de 5 pacotes por dia e retorna os resultados em JSON para o frontend consumir.

---

## Conceito: API JSON

Até agora, as rotas retornavam HTML (páginas prontas). Neste passo criamos rotas que retornam **JSON** — um formato de dados leve que o JavaScript do frontend vai ler e usar para montar a tela dinamicamente.

```json
{
  "success": true,
  "stickers": [
    {"player_name": "Mbappé", "rarity": "legendary", "is_new": true},
    ...
  ],
  "packs_remaining": 4
}
```

**Analogia:** HTML é como um prato de comida pronto. JSON é como os ingredientes separados — o frontend (JavaScript) vai montar o prato na hora, com animações e interatividade que o servidor não consegue fazer.

---

## Arquivos criados/modificados

### `app/utils.py` — lógica de negócio

#### `RARITY_WEIGHTS`
```python
RARITY_WEIGHTS = {
    "common":    70,
    "rare":      25,
    "legendary":  5,
}
```
Pesos de probabilidade. A soma não precisa ser 100 — o Python calcula a proporção automaticamente. Se adicionar uma raridade nova ("epic": 15), o Python reajusta tudo.

#### `get_packs_opened_today(user_id, db)`
```sql
SELECT COUNT(*) FROM pack_openings
WHERE user_id = ? AND date(opened_at) = '2026-06-10'
```
`date(opened_at)` é uma função do SQLite que extrai só a data de um campo datetime. Ao comparar com `date.today().isoformat()`, filtramos só os pacotes de hoje. À meia-noite, a data muda e o contador zera automaticamente — sem nenhum job ou cron.

#### `draw_stickers(db, n)`
```python
sorteadas = random.choices(population, weights=weights, k=n)
```
`random.choices` com `k=n` faz `n` sorteios **com reposição** — a mesma figurinha pode sair duas vezes no mesmo pacote (como na vida real). Os pesos são extraídos da coluna `rarity` de cada figurinha.

#### `award_stickers(user_id, sticker_ids, db)`
Padrão **upsert** manual:
```python
if existing:
    UPDATE user_stickers SET quantity = quantity + 1 WHERE id = ?
else:
    INSERT INTO user_stickers ...
```
O SQLite tem `INSERT OR REPLACE`, mas usamos manual para ter controle total — um `INSERT OR REPLACE` deletaria e recriaria a linha, perdendo o `obtained_at` original.

#### `record_pack_opening(user_id, sticker_ids, db)`
```python
json.dumps([1, 3, 3, 5, 7])  →  "[1, 3, 3, 5, 7]"
```
`json.dumps` serializa a lista Python para uma string JSON. Armazenamos no banco como texto — serve como trilha de auditoria e para contar pacotes abertos hoje.

---

### `app/stickers.py` — novos endpoints

#### `GET /api/pack/remaining`
Retorna quantos pacotes o usuário ainda pode abrir hoje. O frontend usa isso para exibir o contador e desabilitar o botão quando chegar a zero.

#### `POST /api/pack/open`
Fluxo em ordem crítica:

```python
# 1. Busca estado do álbum ANTES de creditar (para calcular is_new corretamente)
ids_antes = {r["sticker_id"] for r in possuidas_antes}

# 2. Sorteia
sorteadas = draw_stickers(db, stickers_per_pack)

# 3. Credita no álbum
award_stickers(current_user.id, ids_sorteados, db)

# 4. Registra o pacote (para o limite diário)
record_pack_opening(current_user.id, ids_sorteados, db)
```

**Por que a ordem importa?** Se buscarmos `ids_antes` depois de `award_stickers`, todas as figurinhas recém-adicionadas já estarão no banco — nenhuma seria marcada como `is_new`. Bug clássico de ordenação.

#### HTTP 429 — Too Many Requests
```python
return jsonify({...}), 429
```
Quando o limite é atingido, retornamos o código HTTP correto para "você fez requests demais". Usar `200` com `success: false` seria impreciso — o status HTTP deve refletir o tipo de resposta.

#### `is_new` — lógica de novidade
```python
vistos_neste_pacote = set()
for s in sorteadas:
    is_new = s["id"] not in ids_antes and s["id"] not in vistos_neste_pacote
    vistos_neste_pacote.add(s["id"])
```
Se o mesmo pacote tiver duas cópias da mesma figurinha nova, só a primeira é `is_new = True`. Isso evita mostrar duas animações de "NOVA!" para a mesma figurinha.

---

## Bug corrigido neste passo

**Problema:** `ids_antes` estava sendo buscado *depois* de `award_stickers`. Resultado: nenhuma figurinha era marcada como nova.

**Correção:** Movemos a query para *antes* do sorteio — capturamos o estado real do álbum antes de qualquer modificação.

**Lição:** Em sistemas que lêem e escrevem no mesmo banco, a ordem das operações importa. Sempre pense: "o que preciso saber antes de modificar?"

---

## Como testar via terminal

```bash
# Com o servidor rodando (python run.py), usando curl:

# Ver pacotes restantes
curl http://127.0.0.1:5000/api/pack/remaining -b cookies.txt

# Abrir um pacote
curl -X POST http://127.0.0.1:5000/api/pack/open -b cookies.txt
```

Ou abra o navegador, faça login e no console do DevTools (F12):
```javascript
fetch('/api/pack/open', { method: 'POST' })
  .then(r => r.json())
  .then(console.log)
```

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| API JSON | Rota que retorna dados (não HTML) para o JavaScript consumir |
| `random.choices` com pesos | Sorteio probabilístico — raridades diferentes têm chances diferentes |
| Sorteio com reposição | Mesma figurinha pode sair duas vezes no pacote |
| Upsert manual | Insert se não existe, Update se já existe |
| `json.dumps` | Serializa lista Python para string JSON |
| HTTP 429 | Código correto para "limite de requisições atingido" |
| Ordem de operações | Ler o estado antes de escrever — bug clássico |
| `set` para lookup O(1) | `sticker_id in ids_antes` é instantâneo com set, lento com list |

---

## Próximo passo

**Passo 6 — UI de Abertura de Pacote:** criaremos a tela com botão "Abrir Pacote" e animação de virar carta usando JavaScript e CSS. O frontend vai consumir o endpoint `POST /api/pack/open` que acabamos de criar.
