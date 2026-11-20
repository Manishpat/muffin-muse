/* Muffin Muse — site interactions (nav, collection, gallery, lightbox, testimonials) */
(function () {
  "use strict";
  var C = window.MM_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  document.documentElement.classList.add("js");

  /* ── Config wiring ── */
  var igUrl = C.instagramUrl || "https://www.instagram.com/";
  $$("[data-ig-link]").forEach(function (a) { a.href = igUrl; });
  $$("[data-ig-handle]").forEach(function (s) { s.textContent = C.instagramHandle || "muffinmuse_i"; });
  var wa = String(C.whatsappNumber || "").replace(/\D/g, "");
  if (wa.length >= 10) {
    var waUrl = "https://wa.me/" + wa + "?text=" + encodeURIComponent("Hi Diksha! I'd like to enquire about a cake from Muffin Muse 🎂");
    $$("[data-wa-link]").forEach(function (a) { a.href = waUrl; a.hidden = false; });
    $(".floaters").classList.add("has-wa");
  }
  var lead = Number(C.minLeadDays || 0);
  $$("[data-lead-text]").forEach(function (s) { s.textContent = lead <= 0 ? "a few hours" : lead + (lead === 1 ? " day" : " days"); });
  $("#year").textContent = new Date().getFullYear();

  /* ── Data ── */
  var CATS = [
    { key: "birthday", name: "Birthday Cakes", desc: "From first candles to fabulous forties — playful, personal and party-ready.", size: "xl", occasion: "Birthday" },
    { key: "wedding", name: "Wedding Cakes", desc: "Tiered, timeless and finished by hand for your big day.", size: "tall", occasion: "Wedding" },
    { key: "anniversary", name: "Anniversary Cakes", desc: "Elegant cakes to toast every year together.", occasion: "Wedding Anniversary" },
    { key: "babyshower", name: "Baby Shower Cakes", desc: "Soft pastels and sweet surprises, gender reveals included.", occasion: "Baby Shower" },
    { key: "kids", name: "Kids' Theme Cakes", desc: "Cartoons, unicorns, superheroes — their favourite world in cake.", occasion: "Birthday", design: "Fondant Theme Cake" },
    { key: "bento", name: "Bento Cakes", desc: "Mini lunchbox cakes made for little moments and big smiles.", design: "Bento Cake", weight: "250 g" },
    { key: "chocolate", name: "Chocolate Cakes", desc: "Ganache drips, truffle layers and deep, dark indulgence.", size: "tall", flavour: "Chocolate Truffle" },
    { key: "floral", name: "Floral Cakes", desc: "Hand-piped blooms in buttercream — a garden on every tier.", size: "wide", design: "Floral Buttercream" },
    { key: "designer", name: "Designer Cakes", desc: "Statement drips, macarons and sculpted details made to impress.", design: "Designer / Custom" },
    { key: "cupcakes", name: "Cupcakes & Desserts", desc: "Swirled cupcakes, jars and dessert boxes for sharing.", design: "Cupcakes & Desserts" }
  ];
  var GALLERY = [
    ["g1", "A trio of celebration cakes", 900, 1350], ["g7", "Rainbow sprinkle layer cake", 900, 821],
    ["g6", "Raspberry layer slice", 900, 1125], ["g8", "Chocolate mousse cake", 900, 1354],
    ["g2", "Black forest naked cake", 900, 1039], ["g10", "Pink frosted cupcakes", 900, 1350],
    ["g4", "Ivory cake with chocolate drip", 900, 696], ["g3", "Cherry-topped chocolate cake", 900, 722],
    ["g9", "Orange glaze entremet", 900, 526], ["g11", "Strawberry dessert jars", 900, 1350],
    ["g5", "Blueberry naked cake", 900, 1350], ["g12", "Cherry vanilla cupcake", 900, 1354]
  ];
  /* Sample testimonials — replace with real customer words in this list. */
  var QUOTES = [
    ["The cake looked exactly like the reference I sent — and tasted even better. Every single guest asked where it was from.", "Priya S.", "1st birthday cake"],
    ["Diksha understood our theme instantly. The eggless chocolate truffle was the softest cake we've ever had.", "Rahul & Neha", "Anniversary cake"],
    ["Booking took two minutes, and she called back the same day to finalise the design. Such a personal experience.", "Ananya M.", "Baby shower cake"],
    ["Our wedding cake was the centrepiece of the evening. Elegant, delicious and delivered right on time.", "Karan & Isha", "Two-tier wedding cake"]
  ];

  /* ── Collection bento ── */
  var bento = $("#bento");
  bento.innerHTML = CATS.map(function (c, i) {
    var cls = "card reveal" + (c.size ? " card--" + c.size : "");
    var big = c.size === "xl" || c.size === "tall" || c.size === "wide";
    return '<article class="' + cls + '">' +
      '<img src="assets/img/' + c.key + (big ? "" : "-sm") + '.webp" alt="' + c.name + ' by Muffin Muse" loading="lazy" decoding="async">' +
      '<span class="card__n">' + String(i + 1).padStart(2, "0") + "</span>" +
      '<div class="card__body"><h3>' + c.name + "</h3><p>" + c.desc + "</p>" +
      '<button type="button" class="card__cta" data-cat="' + c.key + '" aria-label="Enquire about ' + c.name + '">Enquire &amp; book →</button></div></article>';
  }).join("");
  bento.addEventListener("click", function (e) {
    var b = e.target.closest("[data-cat]");
    if (!b) return;
    var cat = CATS.filter(function (c) { return c.key === b.dataset.cat; })[0];
    document.dispatchEvent(new CustomEvent("mm:prefill", { detail: cat }));
    $("#book").scrollIntoView({ behavior: "smooth" });
  });

  /* ── Gallery ── */
  var masonry = $("#masonry"), masonryCols = 0;
  var tiles = GALLERY.map(function (g, i) {
    var b = document.createElement("button");
    b.type = "button"; b.dataset.i = i; b.dataset.caption = g[1]; b.setAttribute("aria-label", "View larger: " + g[1]);
    b.innerHTML = '<img src="assets/img/' + g[0] + '-sm.webp" alt="' + g[1] + '" loading="lazy" decoding="async" width="560" height="' + Math.round(560 * g[3] / g[2]) + '">';
    return b;
  });
  // Balanced masonry: each photo goes into the currently shortest column (by real aspect ratio).
  function layoutMasonry() {
    var w = window.innerWidth, n = w > 1080 ? 4 : w > 640 ? 3 : 2;
    if (n === masonryCols) return;
    masonryCols = n;
    var cols = [], heights = [];
    for (var c = 0; c < n; c++) { var d = document.createElement("div"); d.className = "masonry__col"; cols.push(d); heights.push(0); }
    tiles.forEach(function (t, i) {
      var k = heights.indexOf(Math.min.apply(null, heights));
      cols[k].appendChild(t); heights[k] += GALLERY[i][3] / GALLERY[i][2] + 0.05;
    });
    masonry.innerHTML = ""; cols.forEach(function (d) { masonry.appendChild(d); });
  }
  layoutMasonry();
  var rT; window.addEventListener("resize", function () { clearTimeout(rT); rT = setTimeout(layoutMasonry, 150); });

  /* ── Lightbox ── */
  var lb = $("#lightbox"), lbImg = $("#lbImg"), lbCap = $("#lbCap"), lbIdx = 0;
  function showLb(i) {
    lbIdx = (i + GALLERY.length) % GALLERY.length;
    var g = GALLERY[lbIdx];
    lbImg.src = "assets/img/" + g[0] + ".webp"; lbImg.alt = g[1]; lbCap.textContent = g[1];
  }
  masonry.addEventListener("click", function (e) {
    var b = e.target.closest("[data-i]"); if (!b) return;
    showLb(+b.dataset.i);
    if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
  });
  function closeLb() { if (lb.close) lb.close(); else lb.removeAttribute("open"); }
  $("#lbClose").addEventListener("click", closeLb);
  $("#lbPrev").addEventListener("click", function () { showLb(lbIdx - 1); });
  $("#lbNext").addEventListener("click", function () { showLb(lbIdx + 1); });
  $("#lbCta").addEventListener("click", function () {
    document.dispatchEvent(new CustomEvent("mm:prefill", { detail: { name: "Gallery – " + GALLERY[lbIdx][1] } }));
    closeLb();
  });
  lb.addEventListener("click", function (e) { if (e.target === lb) closeLb(); });
  lb.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") showLb(lbIdx + 1);
    if (e.key === "ArrowLeft") showLb(lbIdx - 1);
  });
  var tx = null;
  lb.addEventListener("touchstart", function (e) { tx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", function (e) {
    if (tx === null) return; var dx = e.changedTouches[0].clientX - tx; tx = null;
    if (Math.abs(dx) > 50) showLb(lbIdx + (dx < 0 ? 1 : -1));
  });

  /* ── Testimonials ── */
  var track = $("#quotesTrack"), dots = $("#qDots"), qi = 0, qTimer;
  track.innerHTML = QUOTES.map(function (q, i) {
    return '<figure class="quote' + (i === 0 ? " is-active" : "") + '" role="group" aria-roledescription="slide" aria-label="' + (i + 1) + " of " + QUOTES.length + '"><blockquote>' + q[0] + "</blockquote><figcaption><strong>" + q[1] + "</strong> · " + q[2] + "</figcaption></figure>";
  }).join("");
  dots.innerHTML = QUOTES.map(function (_, i) { return '<button type="button" role="tab" aria-label="Show testimonial ' + (i + 1) + '" aria-selected="' + (i === 0) + '" data-q="' + i + '"></button>'; }).join("");
  function showQ(i) {
    qi = (i + QUOTES.length) % QUOTES.length;
    $$(".quote", track).forEach(function (el, j) { el.classList.toggle("is-active", j === qi); });
    $$("button", dots).forEach(function (el, j) { el.setAttribute("aria-selected", j === qi); });
  }
  function autoQ() { clearInterval(qTimer); qTimer = setInterval(function () { showQ(qi + 1); }, 7000); }
  $("#qPrev").addEventListener("click", function () { showQ(qi - 1); autoQ(); });
  $("#qNext").addEventListener("click", function () { showQ(qi + 1); autoQ(); });
  dots.addEventListener("click", function (e) { var b = e.target.closest("[data-q]"); if (b) { showQ(+b.dataset.q); autoQ(); } });
  if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) autoQ();

  /* ── Instagram grid ── */
  var ig = ["g10", "ig1", "g6", "ig2", "g3", "g11"];
  $("#instaGrid").innerHTML = ig.map(function (k) {
    return '<a href="' + igUrl + '" target="_blank" rel="noopener" aria-label="See more on Instagram"><img src="assets/img/' + k + '-sm.webp" alt="" loading="lazy" decoding="async"></a>';
  }).join("");

  /* ── Nav ── */
  var nav = $("#nav"), burger = $("#burger"), menu = $("#mobileMenu"), mobileBook = $("#mobileBook");
  var bookSec = $("#book"), hero = $("#home");
  function onScroll() {
    var y = window.scrollY;
    nav.classList.toggle("is-scrolled", y > 20);
    var br = bookSec.getBoundingClientRect();
    var inBook = br.top < window.innerHeight * 0.85 && br.bottom > 0;
    mobileBook.classList.toggle("is-visible", y > hero.offsetHeight * 0.6 && !inBook);
  }
  window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  function setMenu(open) {
    burger.setAttribute("aria-expanded", open); menu.hidden = !open;
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }
  burger.addEventListener("click", function () { setMenu(burger.getAttribute("aria-expanded") !== "true"); });
  menu.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });

  /* current section highlight */
  var links = $$(".nav__links a");
  if ("IntersectionObserver" in window) {
    var secObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) links.forEach(function (a) { a.classList.toggle("is-current", a.getAttribute("href") === "#" + en.target.id); });
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    links.forEach(function (a) { var s = $(a.getAttribute("href")); if (s) secObs.observe(s); });

    /* reveal on scroll */
    var rev = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); rev.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    $$(".reveal").forEach(function (el, i) {
      el.style.transitionDelay = (i % 4) * 70 + "ms";
      rev.observe(el);
    });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("in"); });
  }
})();
