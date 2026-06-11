const btnAbrir      = document.getElementById("btn-abrir");
const packsRestEl   = document.getElementById("packs-restantes");
const resultado     = document.getElementById("resultado");
const cardsContainer = document.getElementById("cards-container");

const RARITY_LABEL = {
    common:    "COMUM",
    rare:      "RARO",
    legendary: "LENDÁRIO",
};

function criarCard(sticker) {
    const card = document.createElement("div");
    card.className = `pack-card-flip rarity-${sticker.rarity}`;

    card.innerHTML = `
        <div class="pack-card-inner">
            <div class="pack-card-frente">
                <span class="pack-card-interrogacao">?</span>
            </div>
            <div class="pack-card-verso">
                ${sticker.is_new ? '<div class="badge-nova">NOVA!</div>' : ""}
                <div class="pack-card-rarity rarity-label-${sticker.rarity}">
                    ${RARITY_LABEL[sticker.rarity] || sticker.rarity}
                </div>
                <div class="pack-card-nome">${sticker.player_name}</div>
                <div class="pack-card-pais">${sticker.country}</div>
            </div>
        </div>
    `;

    return card;
}

function mostrarCards(stickers) {
    cardsContainer.innerHTML = "";
    resultado.style.display = "block";

    stickers.forEach((sticker, index) => {
        const card = criarCard(sticker);
        cardsContainer.appendChild(card);

        setTimeout(() => {
            card.classList.add("virada");
        }, 200 + index * 200);
    });
}

function atualizarContador(restantes) {
    packsRestEl.textContent = restantes;

    const label = btnAbrir.parentElement.querySelector
        ? btnAbrir.parentElement : document;

    if (restantes === 0) {
        btnAbrir.disabled = true;
        btnAbrir.textContent = "Volte amanhã!";
    }
}

const spinner = document.getElementById("spinner-btn");

function setCarregando(sim) {
    btnAbrir.disabled = sim;
    if (spinner) spinner.style.display = sim ? "inline-block" : "none";
    if (sim) {
        btnAbrir.dataset.textoOriginal = btnAbrir.textContent;
        btnAbrir.textContent = " Abrindo...";
        if (spinner) btnAbrir.prepend(spinner);
    }
}

btnAbrir.addEventListener("click", async () => {
    setCarregando(true);

    try {
        const resposta = await fetch("/api/pack/open", { method: "POST" });
        const dados    = await resposta.json();

        if (dados.success) {
            mostrarCards(dados.stickers);
            atualizarContador(dados.packs_remaining);

            if (dados.packs_remaining > 0) {
                setCarregando(false);
                btnAbrir.textContent = "⚽ Abrir Pacote";
            }
        } else {
            if (spinner) spinner.style.display = "none";
            btnAbrir.textContent = "Volte amanhã!";
            packsRestEl.textContent = "0";
        }
    } catch (erro) {
        setCarregando(false);
        btnAbrir.textContent = "⚽ Abrir Pacote";
        alert("Erro de conexão. Tente novamente.");
    }
});
