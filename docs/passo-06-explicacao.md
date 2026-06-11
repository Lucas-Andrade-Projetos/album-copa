# Passo 6 — UI de Abertura de Pacote

## O que foi feito

Criamos a tela de abertura de pacotes. O usuário clica em "Abrir Pacote", o JavaScript busca os dados do backend, e as 5 cartas aparecem viradas uma por vez com animação 3D. Figurinhas novas ganham um badge "NOVA!".

---

## Como funciona (fluxo completo no navegador)

1. Usuário acessa `/pack` — servidor renderiza o HTML com o botão e o contador
2. Usuário clica em "Abrir Pacote"
3. JavaScript desabilita o botão e muda o texto para "Abrindo..."
4. `fetch` envia `POST /api/pack/open` para o servidor
5. Servidor sorteia, credita e retorna JSON com as 5 figurinhas
6. JavaScript cria os cards no DOM e os "vira" um por um (200ms de intervalo)
7. Contador de pacotes restantes é atualizado
8. Botão volta a ficar ativo (se ainda houver pacotes)

---

## Conceitos de JavaScript usados

### `fetch` — requisição assíncrona
```javascript
const resposta = await fetch("/api/pack/open", { method: "POST" });
const dados    = await resposta.json();
```
`fetch` envia uma requisição HTTP sem travar a página. `await` pausa a execução até a resposta chegar — mas o navegador continua respondendo normalmente (não "congela").

**Analogia:** É como pedir uma pizza por telefone. Você faz o pedido (fetch) e continua fazendo outras coisas. Quando toca o interfone (resposta), você vai buscar.

### `async/await`
```javascript
btnAbrir.addEventListener("click", async () => { ... });
```
`async` marca a função como assíncrona. Dentro dela, `await` pode ser usado para esperar Promises. Sem `async/await`, o mesmo código usaria `.then().catch()` — mais verboso e difícil de ler.

### Manipulação do DOM
```javascript
const card = document.createElement("div");
card.className = "pack-card-flip";
card.innerHTML = `<div>...</div>`;
cardsContainer.appendChild(card);
```
`createElement` cria um elemento HTML em memória. `appendChild` o insere na página. `innerHTML` define o conteúdo interno via string (template literal com backtick `` ` ``).

### `setTimeout` escalonado
```javascript
stickers.forEach((sticker, index) => {
    setTimeout(() => {
        card.classList.add("virada");
    }, 200 + index * 200);
});
```
Cada carta vira com um delay diferente: carta 0 → 200ms, carta 1 → 400ms, carta 2 → 600ms... Isso cria o efeito de "uma por vez" sem bloquear o navegador.

### `try/catch` para erros de rede
```javascript
try {
    const resposta = await fetch(...);
    ...
} catch (erro) {
    alert("Erro de conexão.");
}
```
Se o servidor estiver fora do ar ou a internet cair, o `catch` captura o erro e mostra uma mensagem amigável em vez de quebrar silenciosamente.

---

## A animação CSS de virar carta

### O conceito de "dois lados"
```
┌─────────────┐        ┌─────────────┐
│      ?      │  →→→   │   Mbappé    │
│   (frente)  │ vira   │   (verso)   │
└─────────────┘        └─────────────┘
```

### Como funciona com CSS
```css
/* Container que "vira" */
.pack-card-inner {
    transform-style: preserve-3d;  /* ativa modo 3D */
    transition: transform 0.5s ease;
}

/* Ao virar: rotaciona 180° */
.pack-card-flip.virada .pack-card-inner {
    transform: rotateY(180deg);
}

/* Frente: normal */
.pack-card-frente { backface-visibility: hidden; }

/* Verso: começa já rotacionado 180° */
.pack-card-verso {
    transform: rotateY(180deg);
    backface-visibility: hidden;
}
```

`backface-visibility: hidden` faz cada face desaparecer quando está "de costas" para o usuário — sem isso, você veria o texto espelhado do verso aparecer pela frente.

**Analogia:** Coloque duas folhas coladas pelas costas. Com a mão direita em cima, vire — a esquerda some e a direita aparece. CSS faz exatamente isso com matemática de rotação.

### O JavaScript só adiciona uma classe
```javascript
card.classList.add("virada");
```
O JS não calcula nenhuma animação — só adiciona a classe `.virada`. O CSS cuida de todo o visual. Essa separação de responsabilidades é boa prática: **JS controla estado, CSS controla aparência**.

---

## Arquivo `open_pack.html`

```html
<button id="btn-abrir" {% if packs_remaining == 0 %}disabled{% endif %}>
```
O Jinja2 já renderiza o botão como desabilitado se não houver pacotes — o usuário que chega com limite zerado não vê o botão ativo nem por um instante.

```html
<div id="resultado" style="display:none;">
```
A seção de resultado começa invisível. O JavaScript muda para `display: block` após o primeiro pacote aberto.

```html
<script src="{{ url_for('static', filename='js/pack.js') }}"></script>
```
O `<script>` fica no **final** do `{% block content %}`, não no `<head>`. Isso garante que o DOM (botão, containers) já existe quando o JavaScript executar.

---

## Por que `<script>` no final e não no `<head>`?

Se o script fosse no `<head>`, ele executaria antes do HTML do corpo existir. Ao tentar `document.getElementById("btn-abrir")`, retornaria `null` — e qualquer `.addEventListener` quebraria com erro.

Colocar no final do `body` garante que todos os elementos já foram criados.

---

## Conceitos aprendidos neste passo

| Conceito | O que é |
|----------|---------|
| `fetch` | Requisição HTTP assíncrona do navegador |
| `async/await` | Sintaxe moderna para lidar com operações assíncronas |
| DOM manipulation | Criar/inserir elementos HTML via JavaScript |
| `setTimeout` escalonado | Delays progressivos para animar em sequência |
| `preserve-3d` | Ativa modo 3D no CSS para animações de rotação |
| `backface-visibility: hidden` | Esconde o verso de um elemento quando ele está "de costas" |
| Separação JS/CSS | JS controla estado (classes), CSS controla aparência |
| `<script>` no final | Garante que o DOM existe antes do JS executar |

---

## Como testar

```bash
python run.py
```

1. Faça login e clique em **"Abrir Pacote"** na navbar
2. Clique no botão — as 5 cartas devem aparecer virando uma por vez
3. Figurinhas que você não tinha antes mostram o badge **"NOVA!"**
4. O contador decrementou de 5 para 4
5. Clique mais 4 vezes — na última, o botão vira **"Volte amanhã!"**
6. Clique em **"Ver meu álbum →"** — as novas figurinhas aparecem no grid

## Próximo passo

**Passo 7 — Painel Admin:** criaremos uma área protegida onde o admin pode forçar figurinhas, conceder diretamente, zerar limite diário e visualizar todos os usuários.
