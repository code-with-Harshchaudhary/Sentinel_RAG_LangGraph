const root = document.documentElement;
const themeButton = document.getElementById("theme-toggle");
const updateThemeLabel = () => {
  const dark = root.dataset.theme !== "light";
  themeButton.textContent = `Theme[${dark ? "D" : "L"}]`;
  themeButton.setAttribute("aria-label", `Switch to ${dark ? "light" : "dark"} theme`);
};
updateThemeLabel();
themeButton.addEventListener("click", () => {
  root.dataset.theme = root.dataset.theme === "light" ? "dark" : "light";
  try { localStorage.setItem("theme", root.dataset.theme); } catch { /* Storage is optional. */ }
  updateThemeLabel();
});

const search = document.getElementById("paper-search");
const papers = Array.from(document.querySelectorAll("[data-paper]"));
const count = document.getElementById("result-count");
const empty = document.getElementById("no-results");
search.addEventListener("input", () => {
  const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const paper of papers) {
    paper.hidden = !terms.every((term) => paper.dataset.search.includes(term));
    if (!paper.hidden) visible += 1;
  }
  count.textContent = `(${String(visible).padStart(2, "0")})`;
  empty.hidden = visible !== 0;
});
