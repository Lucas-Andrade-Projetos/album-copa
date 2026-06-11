# Passo 8 — Progresso e Conclusão do Álbum

## O que foi feito

A barra de progresso agora é atualizada dinamicamente pelo JavaScript (sem recarregar a página). Um badge mostra quantas figurinhas repetidas o usuário tem. Quando o álbum está 100% completo, um overlay de celebração aparece na tela.

---

## A diferença entre estático e dinâmico

### Antes (Passo 4 — estático)
```
Servidor monta HTML com "2 de 7 (28%)"  →  Navegador exibe
```
O progresso era calculado uma vez, junto com toda a página. Para ver o número atualizado, era preciso recarregar.

### Agora (Passo 8 — dinâmico)
```
Servidor envia HTML com elementos vazios
             ↓
JavaScript busca GET /api/album/status
             ↓
JavaScript atualiza os elementos na tela
```
A página carrega primeiro, depois o JavaScript preenche o progresso. Isso abre a porta para atualizar o progresso *sem recarregar* — por exemplo, após abrir um pacote.

---

## Endpoint `GET /api/album/status`

```python
@bp.route("/api/album/status")
@login_required
def album_status():
    ...
    return jsonify({
        "owned":      obtidas,
        "total":      total,
        "percent":    percent,
        "complete":   obtidas >= total,
        "duplicates": duplicatas,
    })
```

### A query de duplicatas
```sql
SELECT SUM(quantity - 1) FROM user_stickers
WHERE user_id = ? AND quantity > 1
```
`quantity - 1` desconta o "exemplar original" e soma só os extras. Se você tem 3 Mbappés e 2 Vinícius:
- Mbappé contribui com `3 - 1 = 2`
- Vinícius contribui com `2 - 1 = 1`
- Total: `3` duplicatas

O `or 0` em Python trata o caso onde `SUM()` retorna `NULL` — acontece quando não há nenhuma linha com `quantity > 1`.

---

## `album.js` — atualização dinâmica

```javascript
async function carregarStatus() {
    const r = await fetch("/api/album/status");
    const d = await r.json();

    barraFill.style.width   = d.percent + "%";
    barraTexto.textContent  = `${d.owned} de ${d.total} figurinhas`;
    ...
}

document.addEventListener("DOMContentLoaded", carregarStatus);
```

### `DOMContentLoaded`
Evento que dispara quando o HTML foi completamente carregado e analisado — mas **antes** de imagens e CSS externos terminarem de carregar. É o momento ideal para manipular o DOM: os elementos já existem, mas a página ainda não "travou" esperando recursos pesados.

**Analogia:** É como entrar num restaurante assim que o garçom terminou de arrumar as mesas — você pode sentar (DOM pronto), mesmo que a cozinha ainda esteja preparando os pratos (imagens carregando).

### Por que não usar `window.onload`?
`window.onload` espera tudo carregar (imagens, CSS, fontes). `DOMContentLoaded` é mais rápido porque dispara assim que o HTML está pronto. Para manipulação de DOM, o `DOMContentLoaded` é sempre preferível.

---

## O overlay de conclusão

### CSS puro — sem JavaScript para exibir/ocultar
```css
.overlay-completo        { display: flex; }   /* visível por padrão */
.overlay-completo.oculto { display: none;  }  /* oculto quando tem a classe */
```

O HTML começa com `class="overlay-completo oculto"` — oculto. O JavaScript remove a classe `oculto` se o álbum estiver completo:
```javascript
if (d.complete) {
    overlay.classList.remove("oculto");
}
```

### `position: fixed` + `inset: 0`
```css
.overlay-completo {
    position: fixed;
    inset: 0;   /* equivale a: top:0; right:0; bottom:0; left:0 */
}
```
`position: fixed` posiciona em relação à janela do navegador, não à página. Com `inset: 0`, ocupa 100% da tela — por cima de todo o conteúdo. `z-index: 1000` garante que fica acima de tudo.

### Fechar o overlay
```html
<button onclick="document.getElementById('overlay-completo').classList.add('oculto')">
    Ver álbum
</button>
```
Simplesmente adiciona a classe `oculto` de volta — o overlay some. Não precisa de JavaScript separado para isso.

---

## O badge de duplicatas

```javascript
if (d.duplicates > 0) {
    dupBadge.textContent   = `${d.duplicates} repetida${d.duplicates > 1 ? "s" : ""}`;
    dupBadge.style.display = "inline-block";
}
```

O `? "s" : ""` é o **operador ternário** — forma compacta de `if/else` inline. Se `duplicates > 1`, adiciona o "s" no plural. "1 repetida" vs "5 repetidas".

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| Barra de progresso dinâmica | Atualizada pelo JS sem recarregar a página |
| `DOMContentLoaded` | Evento: HTML pronto, imagens ainda carregando |
| `inset: 0` | Atalho CSS para `top/right/bottom/left: 0` |
| `position: fixed` | Posicionamento relativo à janela, não à página |
| `classList.remove/add` | Alternância de classes para mostrar/ocultar elementos |
| Operador ternário | `condição ? valor_se_true : valor_se_false` |
| `SUM(quantity - 1)` | SQL para contar apenas os exemplares excedentes |
| `NULL` em SQL | `SUM()` retorna NULL se não há linhas — tratar com `or 0` |

---

## Como testar

```bash
python run.py
```

1. Faça login como `lucas` → acesse `/album`
2. Barra de progresso mostra o percentual atual
3. Se houver duplicatas, o badge aparece ao lado do texto
4. Como admin: conceda todas as 7 figurinhas ao `lucas`
5. Recarregue `/album` do lucas → overlay de parabéns aparece
6. Clique em "Ver álbum" → overlay fecha, grid visível

## Próximo passo

**Passo 9 — Polish de UX e Tratamento de Erros:** páginas de erro amigáveis (404, 403, 500), flash messages consistentes e responsividade mobile.
