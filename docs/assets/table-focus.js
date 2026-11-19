/* Allow keyboard users to focus horizontally scrollable tables. */
document$.subscribe(() => {
  document.querySelectorAll(".md-typeset__table").forEach((el) => {
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "region");
    el.setAttribute("aria-label", "Таблица с горизонтальной прокруткой");
  });
});
