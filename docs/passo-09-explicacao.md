# Passo 9 — Polish de UX e Tratamento de Erros

## O que foi feito

O site agora trata erros com páginas amigáveis, o botão de abrir pacote mostra um spinner de carregamento, e o layout funciona melhor em telas pequenas.

---

## Handlers de erro do Flask

```python
@app.errorhandler(404)
def not_found(e):
    return render_template("erro.html", codigo=404, titulo="...", descricao="..."), 404
```

**Técnico:** `@app.errorhandler(N)` registra uma função que o Flask chama automaticamente quando aquele código HTTP é lançado — seja por `abort(404)` explícito, seja por uma rota inexistente, seja por exceção interna (500). O segundo elemento do `return` é o status code da resposta (obrigatório — sem ele, Flask enviaria 200 mesmo sendo um erro).

**Simples:** É como configurar um "atendente de reclamações" para cada tipo de problema. Quando algo dá errado, em vez de uma tela técnica bruta, o Flask chama nossa função que manda uma página bonita com a mensagem certa.

### Os três códigos tratados

| Código | Nome | Quando acontece |
|--------|------|-----------------|
| 404 | Not Found | URL não existe no app |
| 403 | Forbidden | Usuário sem permissão (`abort(403)`) |
| 500 | Internal Server Error | Exceção não tratada no código |

---

## Template `erro.html`

Reutiliza o `base.html` (tem navbar, CSS etc.) e recebe três variáveis: `codigo`, `titulo` e `descricao`. Um único template serve para todos os erros — só os textos mudam.

```html
<div class="erro-codigo">{{ codigo }}</div>
<h1 class="erro-titulo">{{ titulo }}</h1>
<p class="erro-desc">{{ descricao }}</p>
```

---

## Spinner de carregamento

### CSS: como funciona o spinner

```css
@keyframes spin {
    to { transform: rotate(360deg); }
}

.spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(0,0,0,0.25);   /* borda cinza ao redor */
    border-top-color: #000;               /* só o topo é escuro */
    border-radius: 50%;                   /* círculo perfeito */
    animation: spin 0.7s linear infinite; /* gira para sempre */
}
```

`@keyframes` define a animação: começa em `0°` e vai até `360°`. `linear` garante velocidade constante (sem acelerar ou desacelerar). `infinite` faz repetir para sempre.

**Analogia:** É como um relógio de ponteiro — a borda cinza é o mostrador, e a borda escura em cima é o ponteiro girando. O CSS faz o ponteiro girar com matemática de rotação.

### JavaScript: controle do estado

```javascript
function setCarregando(sim) {
    btnAbrir.disabled = sim;
    spinner.style.display = sim ? "inline-block" : "none";
}
```

Uma função centraliza o controle: `setCarregando(true)` ativa o spinner e desabilita o botão; `setCarregando(false)` faz o oposto. Isso evita repetir a mesma lógica nos blocos `try` e `catch`.

---

## Responsividade mobile

### Navbar em telas pequenas
```css
@media (max-width: 520px) {
    .navbar-links { gap: 0.9rem; font-size: 0.88rem; }
    .navbar-user  { display: none; }
}
```

`@media` é uma "query de mídia" — regras que só se aplicam quando a tela tem determinado tamanho. Em telas abaixo de 520px, o "Olá, lucas" some (economiza espaço) e os links ficam mais compactos.

### `flex-wrap: wrap` na navbar
Sem `flex-wrap: wrap`, se os links não coubessem na linha, seriam cortados ou causariam scroll horizontal. Com `wrap`, "quebram" para a linha de baixo automaticamente em telas pequenas.

---

## O que é UX?

**UX (User Experience)** é a experiência do usuário ao interagir com o produto. Bom UX significa:
- O usuário sabe o que está acontecendo (spinner → "aguarde")
- Erros têm mensagens compreensíveis (404 → "página não encontrada")
- O layout funciona em qualquer tela (responsividade)
- Ações destrutivas pedem confirmação (limpar álbum)

Código tecnicamente correto com UX ruim é frustrante de usar. UX não é só design — é respeito pelo tempo do usuário.

---

## Como testar

```bash
python run.py
```

1. Acesse `/url-que-nao-existe` → página 404 amigável com botão "Voltar ao início"
2. Logado como usuário comum, acesse `/admin/` → página 403 amigável
3. Abra pacote → botão mostra spinner girando durante o fetch
4. Reduza a janela do navegador → navbar adapta, layout não quebra

---

## Próximo passo

**Passo 10 — Configuração e Segurança:** segredos em variáveis de ambiente, verificação de SQL parametrizado em todo o código, e checklist de segurança.
