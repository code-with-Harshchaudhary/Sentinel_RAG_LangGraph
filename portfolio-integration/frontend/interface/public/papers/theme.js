(() => {
  let preference = "dark";
  try { preference = localStorage.getItem("theme") || "dark"; } catch { /* Storage is optional. */ }
  const light = preference === "light" || (preference === "system" && matchMedia("(prefers-color-scheme: light)").matches);
  document.documentElement.dataset.theme = light ? "light" : "dark";
})();
