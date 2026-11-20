/* Muffin Muse — cake booking wizard
   Sends every booking to the configured inbox via FormSubmit.co.
   Success is shown ONLY after the service confirms delivery. */
(function () {
  "use strict";
  var C = window.MM_CONFIG || {};
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  var form = $("#bookingForm");
  if (!form) return;

  /* ─────────── Options ─────────── */
  var OCCASIONS = [
    ["Birthday", "🎂"], ["Wedding", "💍"], ["Wedding Anniversary", "🥂"], ["Engagement", "💞"], ["Baby Shower", "🍼"],
    ["Baby Welcome", "👣"], ["Naming Ceremony", "🌼"], ["Graduation", "🎓"], ["Housewarming", "🏡"], ["Farewell", "👋"],
    ["Valentine's Day", "❤️"], ["Mother's Day", "🌷"], ["Father's Day", "👔"], ["Raksha Bandhan", "🧿"], ["Diwali", "🪔"],
    ["Christmas", "🎄"], ["New Year", "✨"], ["Holi", "🎨"], ["Eid", "🌙"], ["Onam", "🌸"], ["Pongal", "🍚"],
    ["Karwa Chauth", "🌕"], ["Other", "💫"]
  ];
  var POPULAR = 9;
  var MILESTONES = ["1 Month", "3 Months", "6 Months", "9 Months", "1 Year", "2 Years", "3 Years", "4 Years", "5 Years", "6 Years", "7 Years", "8 Years", "9 Years", "10 Years", "Other"];
  var WEIGHTS = ["250 g", "500 g", "1 kg", "1.5 kg", "2 kg", "3 kg", "Custom"];
  var FLAVOURS = ["Chocolate Truffle", "Belgian Dark Chocolate", "Black Forest", "Red Velvet", "Vanilla Bean", "Butterscotch", "Pineapple", "Fresh Strawberry", "Blueberry", "Mango (seasonal)", "Rasmalai", "Lotus Biscoff", "Coffee Mocha", "Pistachio", "KitKat & Gems", "Not sure – please suggest", "Other"];
  var DESIGNS = ["Whipped Cream", "Buttercream", "Floral Buttercream", "Semi-Fondant", "Fondant Theme Cake", "Photo Print Cake", "Drip Cake", "Tiered Cake", "Bento Cake", "Cupcakes & Desserts", "Designer / Custom", "Not sure – please suggest"];
  var SWATCHES = [["Blush pink", "#F4C2C8"], ["Ivory", "#FBF3E4"], ["Lavender", "#CDB8E3"], ["Baby blue", "#BBD7EE"], ["Mint", "#BFE3CF"], ["Peach", "#F8C9A8"], ["Gold", "#D4AF63"], ["Chocolate", "#5A3A2E"], ["Red", "#C2313B"], ["Black", "#222"]];

  var STEP_NAMES = ["Occasion", "Cake", "Delivery", "Your details", "Review"];

  /* email field labels — this order is the order of the email */
  var LABELS = {
    booking_ref: "Booking reference",
    name: "Full name", phone: "Mobile number", email: "Email", contact_pref: "Preferred contact",
    occasion: "Occasion", occasion_other: "Occasion (details)", birthday_for: "Birthday cake for", birthday_for_other: "Cake for (details)",
    milestone: "Milestone", milestone_other: "Milestone (details)", adult_age: "Turning (age)", anniversary_year: "Anniversary year",
    couple_names: "Couple's names", tiers: "Tiers", baby_theme: "Baby theme", reveal_colour: "Gender reveal colour", baby_name: "Baby's name",
    celebrant_name: "Celebrating", guests: "Approx. guests", collection: "Inspired by",
    weight: "Cake weight", weight_custom: "Custom weight", egg: "Egg / Eggless", flavour: "Flavour", flavour_other: "Flavour (details)",
    design: "Cake design / type", cupcake_qty: "Number of pieces", theme: "Theme", colours: "Colours",
    cake_message: "Message on cake", addons: "Add-ons", budget: "Budget", instructions: "Additional instructions",
    date: "Date required", time_slot: "Preferred time", specific_time: "Exact time", method: "Delivery / Pickup",
    address: "Delivery address", pincode: "Pincode", landmark: "Landmark", customer_area: "Customer area", surprise: "Surprise delivery",
    source: "Found us via", photo_note: "Reference photo"
  };
  var SUMMARY_GROUPS = [
    { title: "Occasion", step: 0, keys: ["occasion", "occasion_other", "birthday_for", "birthday_for_other", "milestone", "milestone_other", "adult_age", "anniversary_year", "couple_names", "tiers", "baby_theme", "reveal_colour", "baby_name", "celebrant_name", "guests", "collection"] },
    { title: "Your cake", step: 1, keys: ["weight", "weight_custom", "egg", "flavour", "flavour_other", "design", "cupcake_qty", "theme", "colours", "cake_message", "addons", "budget", "instructions"] },
    { title: "Delivery", step: 2, keys: ["date", "time_slot", "specific_time", "method", "address", "pincode", "landmark", "customer_area", "surprise"] },
    { title: "Your details", step: 3, keys: ["name", "phone", "email", "contact_pref", "source"] }
  ];

  /* ─────────── Render options ─────────── */
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function chip(name, value, label, type) {
    return '<label class="chip"><input type="' + (type || "radio") + '" name="' + name + '" value="' + esc(value) + '"><span>' + (label || esc(value)) + "</span></label>";
  }
  var occWrap = $("#occasionChips");
  occWrap.className = "chips chips--occ";
  occWrap.innerHTML = OCCASIONS.map(function (o, i) {
    return chip("occasion", o[0], "<em>" + o[1] + "</em>" + esc(o[0])).replace('class="chip"', 'class="chip' + (i >= POPULAR ? " occ-more" : "") + '"');
  }).join("") + '<button type="button" class="link-btn more-btn" id="occMore">+ Show all occasions (Diwali, Raksha Bandhan, Eid…)</button>';
  var occExpanded = false;
  function setOccExpanded(v) {
    occExpanded = v;
    $$(".occ-more", occWrap).forEach(function (el) { el.hidden = !v && !el.querySelector("input").checked; });
    $("#occMore").textContent = v ? "− Show fewer" : "+ Show all occasions (Diwali, Raksha Bandhan, Eid…)";
  }
  $("#occMore").addEventListener("click", function () { setOccExpanded(!occExpanded); });
  $("#milestoneChips").innerHTML = MILESTONES.map(function (m) { return chip("milestone", m); }).join("");
  $("#weightChips").innerHTML = WEIGHTS.map(function (w) { return chip("weight", w, w === "Custom" ? "Custom…" : null); }).join("");
  $("#f_flavour").innerHTML = '<option value="">Choose a flavour</option>' + FLAVOURS.map(function (f) { return "<option>" + esc(f) + "</option>"; }).join("");
  $("#f_design").innerHTML = '<option value="">Choose a style</option>' + DESIGNS.map(function (d) { return "<option>" + esc(d) + "</option>"; }).join("");
  $("#swatches").innerHTML = SWATCHES.map(function (s) { return '<button type="button" title="' + s[0] + '" aria-label="Add ' + s[0] + '" style="background:' + s[1] + '" data-sw="' + s[0] + '"></button>'; }).join("");
  $("#swatches").addEventListener("click", function (e) {
    var b = e.target.closest("[data-sw]"); if (!b) return;
    var inp = $("#f_colours"), cur = inp.value.split(/\s*[,&]\s*/).filter(Boolean);
    if (cur.indexOf(b.dataset.sw) === -1) cur.push(b.dataset.sw);
    inp.value = cur.join(", ").slice(0, 80); save();
  });

  /* ─────────── Helpers ─────────── */
  function controls(name) { return $$('[name="' + name + '"]', form); }
  function val(name) {
    var els = controls(name); if (!els.length) return "";
    var t = els[0].type;
    if (t === "radio") { var c = els.filter(function (e) { return e.checked; })[0]; return c ? c.value : ""; }
    if (t === "checkbox") { return els.filter(function (e) { return e.checked; }).map(function (e) { return e.value; }).join(", "); }
    return (els[0].value || "").trim();
  }
  function isActive(el) { return !el.closest(".cond[hidden]") && !el.closest(".occ-more[hidden]"); }
  function fieldActive(name) { var els = controls(name); return els.length && els.some(isActive); }
  function pad(n) { return String(n).padStart(2, "0"); }
  function ymd(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function prettyDate(s) {
    if (!s) return ""; var p = s.split("-"), d = new Date(+p[0], +p[1] - 1, +p[2]);
    return d.toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "long", year: "numeric" });
  }
  function prettyTime(t) {
    if (!t) return ""; var p = t.split(":"), h = +p[0];
    return (h % 12 || 12) + ":" + p[1] + (h < 12 ? " am" : " pm");
  }

  /* ─────────── Conditional logic ─────────── */
  var conds = $$(".cond", form);
  function evalConds() {
    // two passes so nested conditions settle
    for (var pass = 0; pass < 2; pass++) {
      conds.forEach(function (el) {
        var rule = el.dataset.show, i = rule.indexOf("="), name = rule.slice(0, i), want = rule.slice(i + 1).split("|");
        var v = val(name);
        var parentHidden = el.parentElement && el.parentElement.closest(".cond[hidden]");
        var ok = !parentHidden && (want[0] === "*" ? !!v : want.indexOf(v) !== -1);
        el.hidden = !ok;
      });
    }
    // uncheck a hidden radio (e.g. gender reveal when occasion changes)
    $$(".chip.cond[hidden] input:checked", form).forEach(function (i) { i.checked = false; });
    updateHints();
  }

  /* ─────────── Dates ─────────── */
  var dateInp = $("#f_date");
  var lead = Math.max(0, Number(C.minLeadDays || 0));
  var minD = new Date(); minD.setHours(0, 0, 0, 0); minD.setDate(minD.getDate() + lead);
  var maxD = new Date(minD); maxD.setFullYear(maxD.getFullYear() + 1);
  dateInp.min = ymd(minD); dateInp.max = ymd(maxD);

  function updateHints() {
    var d = dateInp.value;
    $("#dateHint").textContent = d && d >= dateInp.min ? "📅 " + prettyDate(d) : "Earliest available: " + prettyDate(dateInp.min);
    var g = parseInt(val("guests"), 10), gh = $("#guestHint");
    if (g > 0) {
      var kg = g <= 4 ? "500 g" : g <= 10 ? "1 kg" : g <= 15 ? "1.5 kg" : g <= 20 ? "2 kg" : g <= 30 ? "3 kg" : "a tiered cake (" + Math.ceil(g / 10) + " kg+)";
      gh.textContent = "Tip: for " + g + " guests we'd suggest about " + kg + ".";
    } else gh.textContent = "";
    $("#msgCount").textContent = $("#f_message").value.length;
  }

  /* ─────────── Photo upload (client-side optimised) ─────────── */
  var photoFile = null, photoUrl = null;
  var photoInp = $("#f_photo"), drop = $("#drop");
  function setPhotoError(m) { $('[data-err="photo"]').textContent = m || ""; }
  function clearPhoto() {
    photoFile = null; photoInp.value = "";
    if (photoUrl) URL.revokeObjectURL(photoUrl); photoUrl = null;
    drop.classList.remove("has-file"); $(".drop__empty", drop).hidden = false; $(".drop__full", drop).hidden = true;
  }
  function compress(file) {
    return new Promise(function (resolve) {
      if (!/^image\//.test(file.type) || /gif|svg/.test(file.type)) return resolve(file);
      var url = URL.createObjectURL(file), img = new Image();
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight, s = Math.min(1, max / Math.max(w, h));
        var cv = document.createElement("canvas"); cv.width = Math.round(w * s); cv.height = Math.round(h * s);
        cv.getContext("2d").drawImage(img, 0, 0, cv.width, cv.height);
        URL.revokeObjectURL(url);
        cv.toBlob(function (b) {
          if (!b || b.size >= file.size) return resolve(file);
          resolve(new File([b], (file.name || "reference").replace(/\.[^.]+$/, "") + ".jpg", { type: "image/jpeg" }));
        }, "image/jpeg", 0.82);
      };
      img.onerror = function () { URL.revokeObjectURL(url); resolve(file); };
      img.src = url;
    });
  }
  function handleFile(file) {
    setPhotoError("");
    if (!file) return;
    var okType = /^image\//.test(file.type) || /\.(heic|heif|jpe?g|png|webp)$/i.test(file.name);
    if (!okType) { setPhotoError("Please choose an image file (JPG, PNG, WEBP or HEIC)."); photoInp.value = ""; return; }
    compress(file).then(function (f) {
      if (f.size > 5 * 1024 * 1024) { setPhotoError("That photo is over 5 MB even after optimising. Please choose a smaller one or a screenshot."); clearPhoto(); return; }
      photoFile = f;
      if (photoUrl) URL.revokeObjectURL(photoUrl);
      photoUrl = URL.createObjectURL(f);
      $("#photoPreview").src = photoUrl;
      $("#photoName").textContent = file.name || "Reference photo";
      $("#photoSize").textContent = (f.size / 1024 < 1000 ? Math.round(f.size / 1024) + " KB" : (f.size / 1048576).toFixed(1) + " MB") + (f !== file ? " · optimised" : "");
      drop.classList.add("has-file"); $(".drop__empty", drop).hidden = true; $(".drop__full", drop).hidden = false;
    });
  }
  photoInp.addEventListener("change", function () { handleFile(photoInp.files[0]); });
  $("#photoRemove").addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); clearPhoto(); });
  ["dragenter", "dragover"].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.add("is-drag"); }); });
  ["dragleave", "drop"].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.remove("is-drag"); }); });
  drop.addEventListener("drop", function (e) { var f = e.dataTransfer && e.dataTransfer.files[0]; if (f) handleFile(f); });

  /* ─────────── Validation ─────────── */
  var RULES = [
    [0, "occasion", function (v) { return !!v; }, "Please choose the occasion."],
    [0, "occasion_other", function (v) { return v.length >= 2; }, "Please tell us the occasion."],
    [0, "birthday_for", function (v) { return !!v; }, "Please tell us who the cake is for."],
    [0, "birthday_for_other", function (v) { return v.length >= 2; }, "Please tell us who the cake is for."],
    [0, "milestone", function (v) { return !!v; }, "Please choose the milestone."],
    [0, "milestone_other", function (v) { return v.length >= 1; }, "Please tell us the milestone."],
    [0, "adult_age", function (v) { return !v || (+v >= 1 && +v <= 120); }, "Please enter a valid age."],
    [0, "guests", function (v) { return !v || (+v >= 1 && +v <= 2000); }, "Please enter a valid number of guests."],
    [1, "weight", function (v) { return !!v; }, "Please choose a cake weight."],
    [1, "weight_custom", function (v) { return v.length >= 2; }, "Please enter the weight you need."],
    [1, "egg", function (v) { return !!v; }, "Please choose egg or eggless."],
    [1, "flavour", function (v) { return !!v; }, "Please choose a flavour."],
    [1, "flavour_other", function (v) { return v.length >= 2; }, "Please tell us the flavour."],
    [1, "design", function (v) { return !!v; }, "Please choose a cake style."],
    [1, "cake_message", function (v) { return v.length >= 1; }, "Please write the message for the cake."],
    [2, "date", function (v) { return !!v && v >= dateInp.min && v <= dateInp.max; }, function (v) { return !v ? "Please choose the date you need the cake." : v < dateInp.min ? "Please choose " + prettyDate(dateInp.min) + " or later — we need time to bake it fresh." : "Please choose a date within the next year."; }],
    [2, "method", function (v) { return !!v; }, "Please choose delivery or self-pickup."],
    [2, "time_slot", function (v) { return !!v; }, "Please choose a preferred time."],
    [2, "specific_time", function (v) { return !!v; }, "Please choose the exact time."],
    [2, "address", function (v) { return v.length >= 12; }, "Please enter the complete delivery address (house no., street, area, city)."],
    [2, "pincode", function (v) { return /^[1-9]\d{5}$/.test(v); }, "Please enter a valid 6-digit pincode."],
    [3, "name", function (v) { return v.length >= 2 && /[a-zA-Zऀ-ॿ]/.test(v); }, "Please enter your full name."],
    [3, "phone", function (v) { return /^[6-9]\d{9}$/.test(normPhone(v)); }, "Please enter a valid 10-digit Indian mobile number."],
    [3, "email", function (v) { return !v || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }, "Please enter a valid email, or leave it blank."]
  ];
  function normPhone(v) { var d = String(v).replace(/\D/g, ""); if (d.length === 12 && d.indexOf("91") === 0) d = d.slice(2); if (d.length === 11 && d[0] === "0") d = d.slice(1); return d; }
  function showErr(name, msg) {
    var p = $('[data-err="' + name + '"]', form); if (p) p.textContent = msg || "";
    controls(name).forEach(function (el) {
      var f = el.closest(".field"); if (f) f.classList.toggle("is-invalid", !!msg);
      if (el.type !== "radio" && el.type !== "checkbox") el.setAttribute("aria-invalid", msg ? "true" : "false");
    });
  }
  function validateStep(step) {
    var first = null;
    RULES.forEach(function (r) {
      if (r[0] !== step) return;
      if (!fieldActive(r[1])) { showErr(r[1], ""); return; }
      var v = val(r[1]), ok = r[2](v);
      showErr(r[1], ok ? "" : (typeof r[3] === "function" ? r[3](v) : r[3]));
      if (!ok && !first) first = r[1];
    });
    if (first) {
      var el = controls(first).filter(isActive)[0];
      if (el) { (el.closest(".field") || el).scrollIntoView({ behavior: "smooth", block: "center" }); setTimeout(function () { el.focus({ preventScroll: true }); }, 350); }
    }
    return !first;
  }
  form.addEventListener("input", function (e) { if (e.target.name) showErr(e.target.name, ""); });

  /* ─────────── Steps ─────────── */
  var steps = $$(".step", form), cur = 0, maxReached = 0;
  var prevBtn = $("#prevBtn"), nextBtn = $("#nextBtn"), submitBtn = $("#submitBtn");
  function goTo(n, focus) {
    cur = Math.max(0, Math.min(steps.length - 1, n));
    maxReached = Math.max(maxReached, cur);
    steps.forEach(function (s, i) { s.classList.toggle("is-active", i === cur); });
    $$("#stepNav li").forEach(function (li, i) {
      li.classList.toggle("is-active", i === cur); li.classList.toggle("is-done", i < cur);
      if (i === cur) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current");
    });
    $("#progressBar").style.width = ((cur + 1) / steps.length * 100) + "%";
    $("#stepCount").textContent = "Step " + (cur + 1) + " of " + steps.length + " · " + STEP_NAMES[cur];
    prevBtn.hidden = cur === 0;
    nextBtn.hidden = cur === steps.length - 1;
    submitBtn.hidden = cur !== steps.length - 1;
    if (cur === steps.length - 1) renderSummary();
    hideStatus();
    if (focus) {
      var top = $("#booking").getBoundingClientRect().top + window.scrollY - (parseInt(getComputedStyle(document.documentElement).getPropertyValue("--nav-h")) || 70) - 16;
      if (window.scrollY > top || $("#booking").getBoundingClientRect().top < 0) window.scrollTo({ top: top, behavior: "smooth" });
      var t = $(".step__title", steps[cur]); t.setAttribute("tabindex", "-1"); t.focus({ preventScroll: true });
    }
  }
  nextBtn.addEventListener("click", function () { if (validateStep(cur)) { goTo(cur + 1, true); save(); } });
  prevBtn.addEventListener("click", function () { goTo(cur - 1, true); });
  $("#stepNav").addEventListener("click", function (e) {
    var li = e.target.closest("li[data-step]"); if (!li) return;
    var n = +li.dataset.step;
    if (n <= cur) return goTo(n, true);
    for (var s = cur; s < n; s++) { if (!validateStep(s)) { goTo(s, false); return; } }
    goTo(n, true);
  });
  // Enter key on text inputs advances instead of submitting early
  form.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target.tagName === "INPUT" && e.target.type !== "submit") {
      e.preventDefault(); if (cur < steps.length - 1) nextBtn.click();
    }
  });

  /* ─────────── Collect & summary ─────────── */
  function collect() {
    var data = {};
    Object.keys(LABELS).forEach(function (k) {
      if (k === "booking_ref" || k === "photo_note") return;
      if (!fieldActive(k)) return;
      var v = val(k); if (!v) return;
      if (k === "date") v = prettyDate(v) + " (" + v + ")";
      if (k === "specific_time") v = prettyTime(v);
      if (k === "phone") v = "+91 " + normPhone(v);
      if (k === "adult_age") v = v + " years";
      if (k === "anniversary_year") v = v + (["th", "st", "nd", "rd"][(v % 100 - 20) % 10] || ["th", "st", "nd", "rd"][v % 100] || "th") + " anniversary";
      data[k] = v;
    });
    if (fieldActive("want_message") && !val("want_message")) delete data.cake_message;
    return data;
  }
  function renderSummary() {
    var d = collect();
    $("#summary").innerHTML = SUMMARY_GROUPS.map(function (g) {
      var rows = g.keys.filter(function (k) { return d[k]; }).map(function (k) { return "<dt>" + esc(LABELS[k]) + "</dt><dd>" + esc(d[k]) + "</dd>"; }).join("");
      if (g.step === 1 && photoFile) rows += '<dt>Reference photo</dt><dd><img class="sum-photo" src="' + photoUrl + '" alt="Your reference photo"></dd>';
      return '<section class="sum-block"><header><h4>' + g.title + '</h4><button type="button" class="link-btn" data-edit="' + g.step + '">Edit</button></header><dl>' + rows + "</dl></section>";
    }).join("");
  }
  $("#summary").addEventListener("click", function (e) { var b = e.target.closest("[data-edit]"); if (b) goTo(+b.dataset.edit, true); });

  function summaryText(d, ref) {
    var lines = ["🎂 Muffin Muse booking request" + (ref ? " · " + ref : "")];
    SUMMARY_GROUPS.forEach(function (g) {
      lines.push("", "— " + g.title + " —");
      g.keys.forEach(function (k) { if (d[k]) lines.push(LABELS[k] + ": " + d[k]); });
    });
    return lines.join("\n");
  }

  /* ─────────── Draft autosave (per-browser convenience) ─────────── */
  var KEY = "mm_booking_draft_v1";
  function save() {
    try {
      var o = {};
      $$("input[name], select[name], textarea[name]", form).forEach(function (el) {
        if (el.name.charAt(0) === "_" || el.type === "file") return;
        if (el.type === "radio") { if (el.checked) o[el.name] = el.value; }
        else if (el.type === "checkbox") { o[el.name] = o[el.name] || []; if (el.checked) o[el.name].push(el.value); }
        else o[el.name] = el.value;
      });
      localStorage.setItem(KEY, JSON.stringify(o));
    } catch (e) { /* storage unavailable — fine */ }
  }
  function restore() {
    var o; try { o = JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { o = null; }
    if (!o) return;
    Object.keys(o).forEach(function (n) {
      controls(n).forEach(function (el) {
        if (el.type === "radio") el.checked = el.value === o[n];
        else if (el.type === "checkbox") el.checked = Array.isArray(o[n]) && o[n].indexOf(el.value) !== -1;
        else if (!(n === "date" && o[n] && o[n] < dateInp.min)) el.value = o[n];
      });
    });
    if (o.collection) showInspired(o.collection);
  }
  function clearDraft() { try { localStorage.removeItem(KEY); } catch (e) {} }
  var saveT; form.addEventListener("input", function () { clearTimeout(saveT); saveT = setTimeout(save, 400); });
  form.addEventListener("change", function () { evalConds(); setOccExpanded(occExpanded); save(); });
  form.addEventListener("input", updateHints);

  /* ─────────── Prefill from collection cards ─────────── */
  function showInspired(name) {
    $("#f_collection").value = name || "";
    $("#inspired").hidden = !name; $("#inspiredName").textContent = name || "";
  }
  $("#inspiredClear").addEventListener("click", function () { showInspired(""); save(); });
  function setRadio(name, v) { controls(name).forEach(function (el) { el.checked = el.value === v; }); }
  document.addEventListener("mm:prefill", function (e) {
    var c = e.detail || {};
    if ($("#success").hidden === false) resetAll();
    showInspired(c.name);
    if (c.occasion) setRadio("occasion", c.occasion);
    if (c.design) $("#f_design").value = c.design;
    if (c.flavour) $("#f_flavour").value = c.flavour;
    if (c.weight) setRadio("weight", c.weight);
    if (c.occasion === "Birthday" && c.key === "kids") setRadio("birthday_for", "Child");
    evalConds(); setOccExpanded(occExpanded); save(); goTo(0, false);
  });

  /* ─────────── Submission ─────────── */
  var statusBox = $("#formStatus"), sending = false;
  function hideStatus() { statusBox.hidden = true; statusBox.className = "form-status"; statusBox.innerHTML = ""; }
  function makeRef() {
    var d = new Date(), a = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789", r = "";
    for (var i = 0; i < 4; i++) r += a[Math.floor(Math.random() * a.length)];
    return "MM-" + String(d.getFullYear()).slice(2) + pad(d.getMonth() + 1) + pad(d.getDate()) + "-" + r;
  }
  function endpointId() { return String(C.formEndpointId || "").trim(); }

  function buildPayload(ref, withPhoto) {
    var d = collect(), out = {};
    out[LABELS.booking_ref] = ref;
    Object.keys(LABELS).forEach(function (k) { if (d[k]) out[LABELS[k]] = d[k]; });
    out[LABELS.photo_note] = withPhoto ? "Attached to this email" : (photoFile ? "Customer has a reference photo — ask them to share it on WhatsApp/Instagram" : "None");
    out._subject = "🎂 New cake booking · " + (d.name || "") + " · " + (d.occasion || "") + " · " + (val("date") || "") + " · " + ref;
    out._template = "table";
    out._captcha = "false";
    if (d.email) out._replyto = d.email;
    return { fields: out, data: d };
  }

  // 1) Bookings without a photo: FormSubmit AJAX endpoint, JSON response tells us if it was delivered.
  function sendJson(fields) {
    var ctrl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctrl) ctrl.abort(); }, 30000);
    return fetch("https://formsubmit.co/ajax/" + encodeURIComponent(endpointId()), {
      method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(fields), signal: ctrl ? ctrl.signal : undefined
    }).then(function (res) {
      clearTimeout(to);
      return res.json().catch(function () { return {}; }).then(function (j) {
        var ok = res.ok && (j.success === true || j.success === "true");
        if (!ok) throw new Error(j.message || ("The booking service responded with status " + res.status + "."));
        return j;
      });
    }, function (err) {
      clearTimeout(to);
      throw new Error(err && err.name === "AbortError" ? "The booking service took too long to respond." : "We couldn't reach the booking service. Please check your internet connection.");
    });
  }

  // 2) Bookings with a photo: a real multipart form post (FormSubmit supports attachments this way),
  //    sent into a hidden iframe. FormSubmit redirects to our own thanks.html ONLY when the email
  //    was accepted; that page reports back. Anything else (activation page, error, timeout) = failure.
  function sendWithPhoto(fields, ref) {
    return new Promise(function (resolve, reject) {
      var frame = $("#mmUploadFrame"), done = false, graceT, hardT;
      var next = new URL("thanks.html?ref=" + encodeURIComponent(ref), location.href).href;
      var f = document.createElement("form");
      f.method = "POST"; f.enctype = "multipart/form-data"; f.target = frame.name;
      f.action = "https://formsubmit.co/" + encodeURIComponent(endpointId());
      f.className = "hp"; f.setAttribute("aria-hidden", "true");
      var all = Object.assign({}, fields, { _next: next });
      Object.keys(all).forEach(function (k) {
        var t = document.createElement("textarea"); t.name = k; t.value = all[k]; f.appendChild(t);
      });
      var fi = document.createElement("input"); fi.type = "file"; fi.name = "attachment";
      try { var dt = new DataTransfer(); dt.items.add(photoFile); fi.files = dt.files; }
      catch (e) { return reject(new Error("This browser can't attach the photo automatically.")); }
      f.appendChild(fi);
      function finish(ok, msg) {
        if (done) return; done = true;
        clearTimeout(graceT); clearTimeout(hardT);
        window.removeEventListener("message", onMsg); frame.removeEventListener("load", onLoad);
        f.remove();
        ok ? resolve() : reject(new Error(msg));
      }
      function onMsg(e) {
        if (e.origin === location.origin && e.data && e.data.type === "mm-booking-ok" && e.data.ref === ref) finish(true);
      }
      function onLoad() {
        var sameOrigin = false;
        try { sameOrigin = !!frame.contentWindow.location.href && frame.contentWindow.location.href.indexOf("thanks.html") !== -1; } catch (e) { sameOrigin = false; }
        if (sameOrigin) { setTimeout(function () { finish(true); }, 50); return; }
        // landed on a FormSubmit page (activation / error); allow a moment for any redirect
        clearTimeout(graceT);
        graceT = setTimeout(function () { finish(false, "The booking service didn't confirm your photo upload."); }, 8000);
      }
      window.addEventListener("message", onMsg);
      frame.addEventListener("load", onLoad);
      hardT = setTimeout(function () { finish(false, "The photo upload took too long."); }, 60000);
      document.body.appendChild(f);
      f.submit();
    });
  }

  function setLoading(on) {
    sending = on;
    submitBtn.disabled = on; prevBtn.disabled = on;
    submitBtn.classList.toggle("is-loading", on);
    $(".btn__label", submitBtn).textContent = on ? (photoFile ? "Uploading photo & sending…" : "Sending…") : "Send booking request";
  }

  function showError(message, data, ref, photoFailed) {
    var igUrl = C.instagramUrl || "#";
    var wa = String(C.whatsappNumber || "").replace(/\D/g, "");
    var text = summaryText(data, ref);
    statusBox.hidden = false; statusBox.className = "form-status is-error";
    statusBox.innerHTML = "<strong>Your booking was not sent.</strong>" + esc(message) +
      " Nothing has been submitted yet — please try again." +
      '<div class="actions">' +
      '<button type="button" class="btn btn--dark btn--sm" data-act="retry">Try again</button>' +
      (photoFailed ? '<button type="button" class="btn btn--ghost btn--sm" data-act="nophoto">Send without photo</button>' : "") +
      '<button type="button" class="btn btn--ghost btn--sm" data-act="copy">Copy booking details</button>' +
      (wa.length >= 10 ? '<a class="btn btn--ghost btn--sm" target="_blank" rel="noopener" href="https://wa.me/' + wa + "?text=" + encodeURIComponent(text) + '">Send on WhatsApp</a>' : "") +
      '<a class="btn btn--ghost btn--sm" target="_blank" rel="noopener" href="' + esc(igUrl) + '">DM on Instagram</a>' +
      "</div>";
    statusBox.querySelector('[data-act="retry"]').onclick = function () { submit(false); };
    var np = statusBox.querySelector('[data-act="nophoto"]'); if (np) np.onclick = function () { submit(true); };
    statusBox.querySelector('[data-act="copy"]').onclick = function (e) {
      var b = e.currentTarget;
      (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () { b.textContent = "Copied ✓"; }, function () {
        var t = document.createElement("textarea"); t.value = text; document.body.appendChild(t); t.select();
        try { document.execCommand("copy"); b.textContent = "Copied ✓"; } catch (x) { b.textContent = "Copy failed"; } t.remove();
      });
    };
    statusBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function showSuccess(data, ref, withPhoto) {
    $("#successName").textContent = (data.name || "").split(" ")[0] || "lovely";
    $("#successPhone").textContent = data.phone || "your number";
    $("#successRef").textContent = ref;
    var pn = $("#successPhotoNote");
    pn.hidden = !(photoFile && !withPhoto);
    pn.textContent = "Your reference photo wasn't attached — please share it with us on Instagram" + (String(C.whatsappNumber || "").replace(/\D/g, "").length >= 10 ? " or WhatsApp" : "") + " quoting " + ref + ".";
    form.hidden = true; $("#stepNav").hidden = true; $("#inspired").hidden = true;
    $(".booking__progress").hidden = true;
    var s = $("#success"); s.hidden = false; s.focus();
    s.scrollIntoView({ behavior: "smooth", block: "center" });
    clearDraft();
  }

  var lastRef = null;
  function submit(skipPhoto) {
    if (sending) return;
    for (var s = 0; s < steps.length - 1; s++) { if (!validateStep(s)) { goTo(s, false); return; } }
    if (val("_honey")) return; // bot
    if (!endpointId()) { showError("Online booking isn't configured yet.", collect(), "", false); return; }
    if (navigator.onLine === false) { showError("You appear to be offline.", collect(), "", false); return; }
    hideStatus();
    var ref = lastRef || (lastRef = makeRef());
    var withPhoto = !!photoFile && !skipPhoto;
    var p = buildPayload(ref, withPhoto);
    setLoading(true);
    (withPhoto ? sendWithPhoto(p.fields, ref) : sendJson(p.fields))
      .then(function () { setLoading(false); showSuccess(p.data, ref, withPhoto); lastRef = null; })
      .catch(function (err) { setLoading(false); showError(" " + (err && err.message ? err.message : "Something went wrong."), p.data, ref, withPhoto); });
  }
  form.addEventListener("submit", function (e) { e.preventDefault(); if (cur === steps.length - 1) submit(false); else nextBtn.click(); });

  function resetAll() {
    form.reset(); clearPhoto(); showInspired(""); clearDraft();
    form.hidden = false; $("#stepNav").hidden = false; $(".booking__progress").hidden = false; $("#success").hidden = true;
    $$(".is-invalid", form).forEach(function (el) { el.classList.remove("is-invalid"); });
    $$(".err", form).forEach(function (el) { el.textContent = ""; });
    maxReached = 0; evalConds(); setOccExpanded(false); goTo(0, false);
  }
  $("#newBooking").addEventListener("click", function () { resetAll(); goTo(0, true); });

  /* ─────────── Init ─────────── */
  restore();
  evalConds();
  setOccExpanded(false);
  goTo(0, false);
})();
