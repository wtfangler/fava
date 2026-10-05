// Fancy Vanilla site: Minecraft-version tabs, copy buttons, image zoom. Language is chosen by the URL (/pl/, /en/). Everything else is static HTML.
(function () {
  "use strict";
  var root = document.documentElement;

  // ---- Minecraft version tabs in the download box
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".seg [role=tab]"));
  function select(tab) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener("click", function () { select(t); });
    t.addEventListener("keydown", function (e) {
      var next = e.key === "ArrowRight" ? i + 1 : e.key === "ArrowLeft" ? i - 1 : null;
      if (next === null) return;
      var target = tabs[(next + tabs.length) % tabs.length];
      select(target);
      target.focus();
      e.preventDefault();
    });
  });

  // ---- copy buttons
  document.addEventListener("click", function (e) {
    var button = e.target.closest("[data-copy]");
    if (!button) return;
    var text = button.getAttribute("data-copy");
    var done = function () {
      var original = button.innerHTML;
      button.textContent = root.lang === "en" ? "Copied" : "Skopiowano";
      setTimeout(function () { button.innerHTML = original; }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () { /* clipboard blocked: leave the text visible */ });
    }
  });

  // ---- image zoom (lightbox)
  var box = document.getElementById("lightbox");
  if (box && typeof box.showModal === "function") {
    var big = box.querySelector("img");
    document.querySelectorAll("img.zoomable").forEach(function (img) {
      img.tabIndex = 0;
      img.setAttribute("role", "button");
      var open = function () { big.src = img.currentSrc || img.src; big.alt = img.alt; box.showModal(); };
      img.addEventListener("click", open);
      img.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    });
    box.addEventListener("click", function () { box.close(); });
  }
})();
