/* Deadpan Studio on GitHub Pages.
   Reads the queue straight from the repo (GitHub API tree + raw files) so new requests show up within a minute.
   Writing never needs a token: each request becomes a new JSON file that GitHub opens pre-filled for you to commit. */
(function () {
  var OWNER = "Ianeskiii", REPO = "deadpan-studio", BRANCH = "main";
  var RAW = "https://raw.githubusercontent.com/" + OWNER + "/" + REPO + "/" + BRANCH + "/";
  var API = "https://api.github.com/repos/" + OWNER + "/" + REPO;
  var STAGES = ["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"];
  var S = { shorts: [], chars: [], scenes: [], reqs: [], revs: {}, filter: "all", picked: {}, ver: {}, live: true };
  var $ = function (id) { return document.getElementById(id); };

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      var v = attrs[k]; if (v == null || v === false) return;
      if (k === "text") n.textContent = v; else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
    });
    (kids || []).forEach(function (c) { if (c != null) n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function slug(t) { return (t || "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48) || "short"; }
  function ago(t) { var m = Math.round((Date.now() - t) / 60000); return m < 1 ? "just now" : m < 60 ? m + " min ago" : m < 1440 ? Math.round(m / 60) + " h ago" : Math.round(m / 1440) + " d ago"; }
  function fmtMin(m) { m = Math.max(1, Math.round(m)); return m < 60 ? m + " min" : Math.floor(m / 60) + " h " + (m % 60) + " min"; }
  function getJSON(u) { return fetch(u, { cache: "no-store" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function say(id, t, cls) { var m = $(id); m.textContent = t; m.className = "msg " + (cls || ""); }

  /* ---------- load ---------- */
  function listPaths() {
    return getJSON(API + "/git/trees/" + BRANCH + "?recursive=1").then(function (t) {
      S.live = true; return t.tree.map(function (x) { return x.path; });
    }, function () { // API limit or offline: fall back to the index Claude keeps up to date
      S.live = false; return getJSON("shorts/index.json").then(function (ix) { return ix.paths; });
    });
  }
  function load() {
    return listPaths().then(function (paths) {
      var base = S.live ? RAW : "";
      var shortFiles = paths.filter(function (p) { return /^shorts\/[^/]+\/short\.json$/.test(p); });
      var revFiles = paths.filter(function (p) { return /^shorts\/[^/]+\/revision-[^/]+\.json$/.test(p); });
      var reqFiles = paths.filter(function (p) { return /^library\/requests\/[^/]+\.json$/.test(p); });
      var safe = function (p) { return getJSON(base + p).then(function (d) { d.__path = p; return d; }, function () { return null; }); };
      return Promise.all([
        Promise.all(shortFiles.map(safe)), Promise.all(revFiles.map(safe)), Promise.all(reqFiles.map(safe)),
        getJSON(base + "library/characters.json").catch(function () { return []; }),
        getJSON(base + "library/scenes.json").catch(function () { return []; })
      ]);
    }).then(function (r) {
      S.shorts = r[0].filter(Boolean).map(function (s) { s.id = s.id || s.__path.split("/")[1]; return s; })
        .sort(function (a, b) { return (b.updatedAt || b.createdAt || 0) - (a.updatedAt || a.createdAt || 0); });
      S.revs = {}; r[1].filter(Boolean).forEach(function (v) { var id = v.__path.split("/")[1]; (S.revs[id] = S.revs[id] || []).push(v); });
      S.reqs = r[2].filter(Boolean); S.chars = r[3]; S.scenes = r[4];
      $("conn").hidden = S.live; $("conn").textContent = "Showing the last published copy. Brand-new requests may take a few minutes to appear.";
      renderAll();
    }).catch(function () { $("conn").hidden = false; $("conn").textContent = "The studio data couldn't be loaded. Check your connection and reload."; });
  }

  /* ---------- commit helper: GitHub opens a pre-filled new file ---------- */
  function propose(path, obj, msgId, okText) {
    var body = JSON.stringify(obj, null, 2) + "\n";
    var u = "https://github.com/" + OWNER + "/" + REPO + "/new/" + BRANCH + "?filename=" + encodeURIComponent(path);
    var full = u + "&value=" + encodeURIComponent(body);
    var copy = navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(body).catch(function () {}) : Promise.resolve();
    copy.then(function () {
      if (full.length < 7000) { window.open(full, "_blank", "noopener"); say(msgId, okText, "ok"); }
      else { window.open(u, "_blank", "noopener"); say(msgId, "That brief is long, so GitHub opened an empty file. It's copied: paste it in, then click Commit changes.", "ok"); }
    });
  }

  /* ---------- render ---------- */
  function renderAll() { renderShorts(); renderLib("chars"); renderLib("scenes"); renderPickers(); }
  function media(id, f) { return f ? "shorts/" + id + "/" + f : ""; }

  function renderShorts() {
    var list = S.shorts.filter(function (s) {
      return S.filter === "all" || (S.filter === "ready" ? s.status === "ready" : s.status !== "ready");
    });
    $("n-shorts").textContent = S.shorts.length || "";
    var ready = S.shorts.filter(function (s) { return s.status === "ready"; }).length;
    $("shorts-sum").textContent = S.shorts.length ? S.shorts.length + " shorts · " + ready + " ready · " + (S.shorts.length - ready) + " in the queue" : "Nothing yet. Add a short to start.";
    var box = $("list-shorts"); box.textContent = "";
    if (!list.length) box.appendChild(el("div", { class: "empty", text: "No shorts here." }));
    list.forEach(function (s) { box.appendChild(card(s)); });
  }

  function card(s) {
    var vers = s.versions || [], vi = S.ver[s.id] != null ? S.ver[s.id] : vers.length - 1, cur = vers[vi];
    var mon = el("div", { class: "monitor" }, [cur
      ? el("video", { src: media(s.id, cur.video), poster: media(s.id, cur.poster), controls: "", playsinline: "", preload: "none" })
      : el("div", { class: "slate" }, [el("b", { text: s.status === "working" ? (s.progress || 0) + "%" : "—" }), s.status === "working" ? s.stage : "Not made yet"])]);
    var st = s.status || "queued", label = { queued: "Queued", working: "In production", revision: "Revision queued", ready: "Ready", failed: "Failed" }[st] || st;
    var chars = (s.characters || []).map(function (c) { var x = S.chars.filter(function (k) { return k.id === c; })[0]; return x ? x.name : c; });
    var scene = S.scenes.filter(function (k) { return k.id === s.scene; })[0];
    var body = el("div", { class: "body" }, [
      el("div", {}, [el("h2", { text: s.title || s.id }), el("div", { class: "meta" }, [el("span", { class: "pill " + (st === "failed" ? "revision" : st), text: label }),
        el("span", { text: (s.durationMin || "?") + (s.durationMax && s.durationMax !== s.durationMin ? "–" + s.durationMax : "") + " s" }),
        chars.length ? el("span", { text: chars.join(", ") }) : el("span", { text: "Doug" }),
        scene ? el("span", { text: scene.name }) : s.newScene ? el("span", { text: s.newScene }) : null,
        s.episode ? el("span", { class: "tag", text: s.episode }) : null])]),
      descNode(s)
    ]);
    if (st !== "ready") {
      var idx = Math.max(0, Math.min(STAGES.length - 1, s.stageIndex || 0));
      var eta = st === "working" && s.etaMinutes != null ? "About " + fmtMin(s.etaMinutes - (Date.now() - (s.updatedAt || Date.now())) / 60000) + " left"
        : st === "working" ? "Working" : st === "failed" ? (s.note || "Couldn't be made") : "Waiting. Say “run the queue” in any Claude account with the repo attached.";
      body.appendChild(el("div", { class: "strip" }, [
        el("div", { class: "bar", role: "progressbar", "aria-valuemin": 0, "aria-valuemax": 100, "aria-valuenow": s.progress || 0 }, [el("i", { style: "width:" + (s.progress || 0) + "%" })]),
        el("div", { class: "meta" }, [el("span", { class: "eta", text: eta }), s.updatedAt ? el("span", { text: "Updated " + ago(s.updatedAt) }) : null, s.note && st !== "failed" ? el("span", { text: s.note }) : null]),
        el("div", { class: "stages" }, STAGES.slice(1).map(function (n, i) { return el("span", { class: i + 1 < idx ? "done" : i + 1 === idx && st === "working" ? "now" : "", text: n }); }))]));
    }
    if (vers.length) {
      var vrow = el("div", { class: "vers" }, [el("span", { class: "tag", text: "VERSIONS" })]);
      vers.forEach(function (v, i) { vrow.appendChild(el("button", { type: "button", "aria-pressed": String(i === vi), text: "v" + v.v, title: v.notes || "", onclick: function () { S.ver[s.id] = i; renderShorts(); } })); });
      if (cur) vrow.appendChild(el("span", { class: "meta", text: (cur.seconds ? cur.seconds + " s · " : "") + (cur.notes || "") }));
      body.appendChild(vrow);
    }
    var revs = (s.revisions || []).concat((S.revs[s.id] || []).filter(function (r) { return !(s.revisions || []).some(function (x) { return x.at === r.at; }); }));
    if (revs.length) body.appendChild(el("div", { class: "revs" }, revs.map(function (r) { return el("div", { class: "rev" + (r.done ? "" : " open"), text: (r.done ? "Done in v" + (r.doneIn || "?") + ": " : "Requested: ") + r.text }); })));
    var act = el("div", { class: "actions" });
    if (cur) act.appendChild(el("a", { class: "btn", href: media(s.id, cur.video), download: slug(s.title) + "_v" + cur.v + ".mp4", text: "Download v" + cur.v }));
    if (vers.length && st !== "working") {
      var ta = el("textarea", { maxlength: 4000, placeholder: "What should change? e.g. hold the stare half a second longer", "aria-label": "Revision notes for " + (s.title || s.id) });
      var mid = "rev-msg-" + s.id, m = el("span", { class: "msg", id: mid, role: "status" });
      body.appendChild(el("details", { class: "revise" }, [el("summary", { text: "Request a revision" }), ta, el("div", { class: "row" }, [
        el("button", { class: "btn primary", type: "button", text: "Queue revision", onclick: function () {
          var t = ta.value.trim(); if (t.length < 5) return say(mid, "Describe what should change.", "err");
          var at = Date.now(); propose("shorts/" + s.id + "/revision-" + at + ".json", { text: t, at: at, done: false }, mid, "GitHub opened in a new tab. Click Commit changes to queue the revision.");
        } }), m])]));
    }
    if (act.childNodes.length) body.appendChild(act);
    return el("article", { class: "short" }, [mon, body]);
  }
  function descNode(s) {
    var p = el("p", { class: "desc clamp", text: s.description || "" });
    if ((s.description || "").length < 220) return p;
    var b = el("button", { class: "btn", type: "button", text: "Show full brief", style: "justify-self:start;padding:3px 10px;font-size:13px", onclick: function () { var c = p.classList.toggle("clamp"); b.textContent = c ? "Show full brief" : "Show less"; } });
    return el("div", { style: "display:grid;gap:6px" }, [p, b]);
  }

  function renderLib(kind) {
    var rows = kind === "chars" ? S.chars : S.scenes, want = kind === "chars" ? "character" : "scene";
    var pend = S.reqs.filter(function (r) { return r.kind === want && !rows.some(function (x) { return x.name === r.name; }); });
    $(kind === "chars" ? "n-chars" : "n-scenes").textContent = rows.length || "";
    var box = $(kind === "chars" ? "list-chars" : "list-scenes"); box.textContent = "";
    rows.concat(pend.map(function (r) { return { name: r.name, description: r.description, status: "requested" }; })).forEach(function (c) {
      var pic = el("div", { class: "pic", text: c.image ? "" : "to be built" }); if (c.image) pic.style.backgroundImage = "url(" + c.image + ")";
      var tag = c.status === "requested" ? "REQUESTED" : kind === "chars" ? (c.role || "CAST").toUpperCase() + (c.voice ? " · VOICE " + c.voice : "") : (c.usedIn ? "USED IN " + c.usedIn.toUpperCase() : "SET");
      box.appendChild(el("article", { class: "card" + (kind === "chars" ? " char" : "") }, [pic, el("div", { class: "in" }, [
        el("h3", {}, [c.color && /^#[0-9a-fA-F]{6}$/.test(c.color) ? el("span", { class: "swatch", style: "background:" + c.color }) : null, c.name || c.id]),
        el("p", { text: c.description || "" }), el("span", { class: "tag", text: tag })])]));
    });
    if (!box.childNodes.length) box.appendChild(el("div", { class: "empty", text: "Nothing here yet." }));
  }
  function renderPickers() {
    var pick = $("pick-chars"); pick.textContent = "";
    S.chars.filter(function (c) { return c.status !== "requested" && c.pickable !== false; }).forEach(function (c) {
      var dot = el("span", { class: "dot" }); if (c.image) dot.style.backgroundImage = "url(" + c.image + ")";
      pick.appendChild(el("button", { type: "button", class: "chip", "aria-pressed": String(!!S.picked[c.id]), onclick: function () { S.picked[c.id] = !S.picked[c.id]; renderPickers(); } }, [dot, c.name]));
    });
    var sel = $("in-scene"), v = sel.value; sel.textContent = ""; sel.appendChild(el("option", { value: "", text: "Let Claude pick or build one" }));
    S.scenes.forEach(function (sc) { sel.appendChild(el("option", { value: sc.id, text: sc.name })); }); sel.value = v;
  }

  /* ---------- forms ---------- */
  $("f-new").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var title = $("in-title").value.trim(), desc = $("in-desc").value.trim();
    if (title.length < 3) return say("msg-new", "Give the short a title.", "err");
    if (desc.length < 10) return say("msg-new", "Describe what happens in the short.", "err");
    var a = +$("in-dmin").value || 15, b = +$("in-dmax").value || a; if (b < a) { var t = a; a = b; b = t; }
    var id = slug(title), n = 2; while (S.shorts.some(function (s) { return s.id === id; })) id = slug(title).slice(0, 44) + "-" + n++;
    var now = Date.now();
    propose("shorts/" + id + "/short.json", { id: id, title: title, description: desc, durationMin: a, durationMax: b,
      characters: Object.keys(S.picked).filter(function (k) { return S.picked[k]; }), newCharacters: $("in-newchars").value.trim(),
      scene: $("in-scene").value, newScene: $("in-newscene").value.trim(), reference: $("in-ref").value.trim(),
      status: "queued", stage: "Queued", stageIndex: 0, progress: 0, etaMinutes: null, note: "", versions: [], revisions: [], createdAt: now, updatedAt: now },
      "msg-new", "GitHub opened in a new tab. Click Commit changes to add it to the queue.");
  });
  function addLib(form, kind, nameId, descId, msgId) {
    $(form).addEventListener("submit", function (ev) {
      ev.preventDefault();
      var n = $(nameId).value.trim(), d = $(descId).value.trim(); if (n.length < 2 || d.length < 5) return say(msgId, "Add a name and a short description.", "err");
      propose("library/requests/" + kind + "-" + slug(n) + ".json", { kind: kind, name: n, description: d, at: Date.now() }, msgId, "GitHub opened in a new tab. Click Commit changes to send the request.");
    });
  }
  addLib("f-char", "character", "c-name", "c-desc", "msg-char"); addLib("f-scene", "scene", "s-name", "s-desc", "msg-scene");
  $("filters").addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (!b) return; S.filter = b.dataset.f; $("filters").querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); renderShorts(); });

  /* ---------- routing ---------- */
  function route() {
    var v = (location.hash || "#shorts").slice(1); if (!$("view-" + v)) v = "shorts";
    document.querySelectorAll(".view").forEach(function (s) { s.hidden = s.id !== "view-" + v; });
    document.querySelectorAll("nav.tabs a").forEach(function (a) { a.setAttribute("aria-current", a.dataset.view === v ? "page" : "false"); });
  }
  window.addEventListener("hashchange", route); route();
  load();
  setInterval(function () { if (document.visibilityState === "visible" && S.shorts.some(function (s) { return s.status === "working"; })) load(); }, 120000);
})();
