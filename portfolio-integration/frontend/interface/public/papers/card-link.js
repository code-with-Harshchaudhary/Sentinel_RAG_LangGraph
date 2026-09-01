// The collection is an independent static route, not a route in the archived
// Next bundle. Navigate normally instead of asking that bundle for missing RSC.
document.addEventListener("click", (event) => {
  const link = event.target instanceof Element ? event.target.closest('a[href="/papers/"]') : null;
  if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  event.stopImmediatePropagation();
  window.location.assign(link.href);
}, true);
