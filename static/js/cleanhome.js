/* =========================================================
   CLEANHOME — Scripts globaux
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  /* =====================================================
     1. Apparition progressive
     ===================================================== */
  if (!reduceMotion) {
    const revealables = document.querySelectorAll(
      ".hero, .card, .auth-card, .confirm-card, .reservation, .form-card, .summary, .service-image, .page-head, .table-wrap"
    );
    revealables.forEach((el, index) => {
      el.classList.add("reveal");
      el.style.animationDelay = `${Math.min(index * 0.06, 0.36)}s`;
    });
  }

  /* =====================================================
     2. Filtres de catégories (page catalogue)
     ===================================================== */
  const categories = document.querySelectorAll(".category");
  const cards = document.querySelectorAll(".card[data-category]");

  if (categories.length && cards.length) {
    categories.forEach((category) => {
      category.addEventListener("click", () => {
        categories.forEach((c) => c.classList.remove("active"));
        category.classList.add("active");

        const value = category.dataset.category;
        cards.forEach((card) => {
          const match = value === "Tous" || card.dataset.category === value;
          card.classList.toggle("is-filtered", !match);
        });
      });
    });
  }

  /* =====================================================
     3. Changement de statut (page admin réservations)
     ===================================================== */
  const statusSelects = document.querySelectorAll(".status-select");

  if (statusSelects.length) {
    statusSelects.forEach((select) => {
      select.addEventListener("change", () => {
        const wrap = select.parentElement;
        ["pending", "confirmed", "done", "cancelled"].forEach((c) => {
          select.classList.remove(c);
          wrap.classList.remove(c);
        });
        select.classList.add(select.value);
        wrap.classList.add(select.value);

        const tr = select.closest("tr");
        if (tr) tr.dataset.status = select.value;
      });
    });
  }

  /* =====================================================
     4. Filtres par statut (page admin réservations)
     ===================================================== */
  const filters = document.querySelectorAll(".filter");
  const rows = document.querySelectorAll("tbody tr[data-status]");

  if (filters.length && rows.length) {
    filters.forEach((filter) => {
      filter.addEventListener("click", () => {
        filters.forEach((f) => f.classList.remove("active"));
        filter.classList.add("active");

        const value = filter.dataset.filter;
        rows.forEach((row) => {
          row.style.display =
            value === "all" || row.dataset.status === value ? "" : "none";
        });
      });
    });
  }

  /* =====================================================
     5. Aperçu d'image uploadée
     ===================================================== */
  const fileInput = document.querySelector('input[type="file"]');
  const uploadLabel = document.querySelector(".upload-text strong");

  if (fileInput && uploadLabel) {
    fileInput.addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (file) {
        uploadLabel.textContent = file.name;
      }
    });
  }
});
