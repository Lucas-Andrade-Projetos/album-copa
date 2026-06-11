async function carregarStatus() {
    try {
        const r = await fetch("/api/album/status");
        const d = await r.json();

        const barraFill   = document.getElementById("progress-fill");
        const barraTexto  = document.getElementById("progress-texto");
        const barraPercent = document.getElementById("progress-percent");
        const dupBadge    = document.getElementById("dup-badge");
        const overlay     = document.getElementById("overlay-completo");

        if (barraFill)    barraFill.style.width     = d.percent + "%";
        if (barraTexto)   barraTexto.textContent     = `${d.owned} de ${d.total} figurinhas`;
        if (barraPercent) barraPercent.textContent   = d.percent + "%";

        if (dupBadge) {
            if (d.duplicates > 0) {
                dupBadge.textContent    = `${d.duplicates} repetida${d.duplicates > 1 ? "s" : ""}`;
                dupBadge.style.display  = "inline-block";
            } else {
                dupBadge.style.display  = "none";
            }
        }

        if (overlay && d.complete) {
            overlay.classList.remove("oculto");
        }

    } catch (e) {
        console.error("Erro ao carregar status do álbum:", e);
    }
}

document.addEventListener("DOMContentLoaded", carregarStatus);
