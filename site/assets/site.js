// Fancy Vanilla site: Minecraft-version tabs, copy buttons, image zoom. Language is chosen by the URL (/pl/, /en/). Everything else is static HTML.
(function () {
  "use strict";
  var root = document.documentElement;

  // ---- preloader: progress follows real loading (images, fonts, window load), shown once per browser session
  var pre = document.getElementById("preloader");
  if (pre && root.classList.contains("js-preload")) {
    var bar = pre.querySelector("i"), started = Date.now(), finished = false;
    var imgs = Array.prototype.slice.call(document.images).filter(function (i) { return i.loading !== "lazy" && !i.closest("#preloader"); });
    var total = imgs.length + 2, loaded = 0;
    var step = function () { loaded += 1; if (bar) bar.style.width = Math.min(96, Math.round(100 * loaded / total)) + "%"; };
    imgs.forEach(function (i) { if (i.complete) { step(); } else { i.addEventListener("load", step); i.addEventListener("error", step); } });
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(step); } else { step(); }
    var finish = function () {
      if (finished) return;
      finished = true;
      if (bar) bar.style.width = "100%";
      var wait = Math.max(0, 650 - (Date.now() - started));
      setTimeout(function () {
        pre.classList.add("done");
        try { sessionStorage.setItem("fv-pre", "1"); } catch (e) { /* private mode */ }
        setTimeout(function () { root.classList.remove("js-preload"); }, 500);
      }, wait);
    };
    if (document.readyState === "complete") { finish(); } else { window.addEventListener("load", finish); }
    setTimeout(finish, 5000); // never trap the visitor behind the loader
  }

  // ---- Minecraft version tabs in the download box: sliding highlight, cross-fade, smooth height
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".seg [role=tab]"));
  var seg = document.querySelector(".seg"), box = document.querySelector(".panels");
  if (seg) { seg.style.setProperty("--n", tabs.length); }
  function active() { return document.getElementById((tabs.filter(function (t) { return t.getAttribute("aria-selected") === "true"; })[0] || tabs[0]).getAttribute("aria-controls")); }
  function fit() {
    if (!box) return;
    var tallest = 0;
    Array.prototype.forEach.call(box.children, function (p) { tallest = Math.max(tallest, p.offsetHeight); });
    box.style.minHeight = tallest + "px";
  }
  function select(tab, animate) {
    tabs.forEach(function (t, i) {
      var on = t === tab;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      if (on && seg) { seg.style.setProperty("--i", i); }
      var panel = document.getElementById(t.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    fit(animate !== false);
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
  if (tabs.length) {
    select(tabs[0], false);
    window.addEventListener("resize", function () { fit(false); });
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(function () { fit(false); }); }
  }

  // ---- reveal on scroll
  var reveal = Array.prototype.slice.call(document.querySelectorAll(".band .wrap > *, .foot-grid > *"));
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reveal.length && "IntersectionObserver" in window && !calm) {
    var seen = new Map();
    reveal.forEach(function (el) {
      var n = (seen.get(el.parentNode) || 0);
      seen.set(el.parentNode, n + 1);
      el.style.setProperty("--d", Math.min(n, 5) * 90 + "ms");
      el.classList.add("rv");
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("in"); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    reveal.forEach(function (el) { io.observe(el); });
  }

  // ---- smooth wheel scrolling (Lenis): light, off for reduced motion; touch keeps native scrolling
  var lenis = null;
  if (window.Lenis && !calm) {
    lenis = new window.Lenis({ lerp: 0.14, wheelMultiplier: 0.95, smoothWheel: true, anchors: false });
    var raf = function (time) { lenis.raf(time); requestAnimationFrame(raf); };
    requestAnimationFrame(raf);
    var header = document.querySelector(".top");
    document.addEventListener("click", function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a || a.getAttribute("href") === "#") return;
      var target = document.querySelector(a.getAttribute("href"));
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target, { offset: -(header ? header.offsetHeight : 0) - 8, duration: 1.1 });
      if (history.pushState) { history.pushState(null, "", a.getAttribute("href")); }
    });
  }

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

  // ---- image zoom (lightbox) with fade in/out
  var lb = document.getElementById("lightbox");
  if (lb && typeof lb.showModal === "function") {
    var big = lb.querySelector("img");
    var closeLb = function () {
      if (!lb.open || lb.classList.contains("closing")) return;
      if (calm) { lb.close(); return; }
      lb.classList.add("closing");
      setTimeout(function () { lb.classList.remove("closing"); lb.close(); if (lenis) { lenis.start(); } }, 220);
    };
    document.querySelectorAll("img.zoomable").forEach(function (img) {
      img.tabIndex = 0;
      img.setAttribute("role", "button");
      var open = function () { big.src = img.currentSrc || img.src; big.alt = img.alt; lb.showModal(); if (lenis) { lenis.stop(); } };
      img.addEventListener("click", open);
      img.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } });
    });
    lb.addEventListener("click", closeLb);
    lb.addEventListener("cancel", function (e) { e.preventDefault(); closeLb(); });
  }
})();
