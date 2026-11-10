/* Deadpan Studio on GitHub Pages.
   Reads the queue straight from the repo (GitHub API tree + raw files) so new requests show up within a minute.
   Writing never needs a token: each request becomes a new JSON file that GitHub opens pre-filled for you to commit. */
(function () {
  var OWNER = "Ianeskiii", REPO = "deadpan-studio", BRANCH = "main";
  var RAW = "https://raw.githubusercontent.com/" + OWNER + "/" + REPO + "/" + BRANCH + "/";
  var API = "https://api.github.com/repos/" + OWNER + "/" + REPO;
  var STAGES = ["Queued", "Script & timing", "Voices", "Set & cast", "Animation", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"];
  var STICKY_STAGES = ["Queued", "Writing narration", "Needs audio", "Timing", "Scenes", "Test frames", "Rendering", "Sound & edit", "Final check", "Ready"];
  var CHANNELS = { "deadpan-doug": "Deadpan Doug", sticky: "Sticky" };
  var S = { shorts: [], chars: [], scenes: [], reqs: [], revs: {}, narr: {}, mp3: {}, filter: "all", chFilter: "all", channel: "deadpan-doug", picked: {}, ver: {}, live: true };
  var $ = function (id) { return document.getElementById(id); };
  /* Local mode: the site is served by tools/local_studio.py on your own PC (not GitHub Pages).
     Everything is read from and saved to the local folder, and Claude Code runs on the PC. */
  var LOCAL = !/\.github\.io$/i.test(location.hostname) && /^https?:$/.test(location.protocol);

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
  function chanOf(s) { return s.channel || "deadpan-doug"; }
  function getText(u) { return fetch(u, { cache: "no-store" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); }); }
  /* Sticky shorts: which state the card is in. */
  function stickyState(s) {
    var st = s.status || "queued", pend = (S.revs[s.id] || []).concat((s.revisions || []).filter(function (r) { return !r.done; }));
    if (pend.some(function (r) { return r.kind === "narration"; })) return "writing";
    if (st === "needs-audio") return S.mp3[s.id] ? "audio-in" : "needs";
    if (st === "queued" || (st === "working" && (s.stageIndex || 0) <= 1)) return "writing";
    if (st === "working" || st === "revision") return "video";
    return st; // ready / failed
  }
  function getJSON(u) { return fetch(u, { cache: "no-store" }).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }); }
  function say(id, t, cls) { var m = $(id); m.textContent = t; m.className = "msg " + (cls || ""); }

  /* ---------- load ---------- */
  function listPaths() {
    if (LOCAL) return getJSON("api/files").then(function (ix) { S.live = true; return ix.paths; });
    return getJSON(API + "/git/trees/" + BRANCH + "?recursive=1").then(function (t) {
      S.live = true; return t.tree.map(function (x) { return x.path; });
    }, function () { // API limit or offline: fall back to the index Claude keeps up to date
      S.live = false; return getJSON("shorts/index.json").then(function (ix) { return ix.paths; });
    });
  }
  function load() {
    return listPaths().then(function (paths) {
      var base = S.live && !LOCAL ? RAW : "";
      var shortFiles = paths.filter(function (p) { return /^shorts\/[^/]+\/short\.json$/.test(p); });
      var revFiles = paths.filter(function (p) { return /^shorts\/[^/]+\/revision-[^/]+\.json$/.test(p); });
      var reqFiles = paths.filter(function (p) { return /^library\/requests\/[^/]+\.json$/.test(p); });
      var narrFiles = paths.filter(function (p) { return /^shorts\/[^/]+\/narration\.txt$/.test(p); });
      S.mp3 = {}; paths.forEach(function (p) { var m = /^shorts\/([^/]+)\/[^/]+\.mp3$/i.exec(p); if (m) S.mp3[m[1]] = true; });
      var safe = function (p) { return getJSON(base + p).then(function (d) { d.__path = p; return d; }, function () { return null; }); };
      return Promise.all([
        Promise.all(shortFiles.map(safe)), Promise.all(revFiles.map(safe)), Promise.all(reqFiles.map(safe)),
        getJSON(base + "library/characters.json").catch(function () { return []; }),
        getJSON(base + "library/scenes.json").catch(function () { return []; }),
        Promise.all(narrFiles.map(function (p) { return getText(base + p).then(function (t) { return [p.split("/")[1], t]; }, function () { return null; }); }))
      ]);
    }).then(function (r) {
      S.shorts = r[0].filter(Boolean).map(function (s) { s.id = s.id || s.__path.split("/")[1]; return s; })
        .sort(function (a, b) { return (b.updatedAt || b.createdAt || 0) - (a.updatedAt || a.createdAt || 0); });
      S.revs = {}; r[1].filter(Boolean).forEach(function (v) { var id = v.__path.split("/")[1]; (S.revs[id] = S.revs[id] || []).push(v); });
      S.reqs = r[2].filter(Boolean); S.chars = r[3]; S.scenes = r[4];
      S.narr = {}; r[5].filter(Boolean).forEach(function (x) { S.narr[x[0]] = x[1].trim(); });
      $("conn").hidden = S.live || LOCAL; $("conn").textContent = "Showing the last published copy. Brand-new requests may take a few minutes to appear.";
      renderAll();
    }).catch(function () { $("conn").hidden = false; $("conn").textContent = "The studio data couldn't be loaded. Check your connection and reload."; });
  }

  /* ---------- commit helper: GitHub opens a pre-filled new file ---------- */
  function propose(path, obj, msgId, okText) {
    var body = JSON.stringify(obj, null, 2) + "\n";
    if (LOCAL) return saveLocal(path, body, msgId);
    var u = "https://github.com/" + OWNER + "/" + REPO + "/new/" + BRANCH + "?filename=" + encodeURIComponent(path);
    var full = u + "&value=" + encodeURIComponent(body);
    var copy = navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(body).catch(function () {}) : Promise.resolve();
    copy.then(function () {
      if (full.length < 7000) { window.open(full, "_blank", "noopener"); say(msgId, okText, "ok"); }
      else { window.open(u, "_blank", "noopener"); say(msgId, "That brief is long, so GitHub opened an empty file. It's copied: paste it in, then click Commit changes.", "ok"); }
    });
  }

  function saveLocal(path, body, msgId) {
    say(msgId, "Saving…");
    return fetch("api/file", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path: path, content: body }) })
      .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || r.status); return j; }); })
      .then(function () {
        say(msgId, "Saved. Claude starts on it right away; progress shows on the card.", "ok");
        if (msgId === "msg-new") { $("in-title").value = ""; $("in-desc").value = ""; if ($("in-notes")) $("in-notes").value = ""; }
        load(); localStatus();
      }, function (e) { say(msgId, "Couldn't save: " + e.message, "err"); });
  }
  function uploadLocal(s, mid) {
    var inp = el("input", { type: "file", accept: ".mp3,audio/mpeg", style: "display:none" });
    inp.addEventListener("change", function () {
      var f = inp.files[0]; if (!f) return;
      if (!/\.mp3$/i.test(f.name)) return say(mid, "Choose an .mp3 file.", "err");
      say(mid, "Uploading " + f.name + "…");
      fetch("api/upload?id=" + encodeURIComponent(s.id) + "&name=" + encodeURIComponent(f.name), { method: "POST", body: f })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || r.status); return j; }); })
        .then(function () { say(mid, "Uploaded. Claude starts making the video now.", "ok"); load(); localStatus(); },
              function (e) { say(mid, "Upload failed: " + e.message, "err"); });
    });
    document.body.appendChild(inp); inp.click();
    setTimeout(function () { if (inp.parentNode) inp.parentNode.removeChild(inp); }, 600000);
  }
  /* local status bar: is Claude working, idle or missing? */
  function localStatus() {
    if (!LOCAL) return;
    var bar = $("local-bar");
    if (!bar) { bar = el("div", { id: "local-bar", class: "note", role: "status" }); var c = $("conn"); c.parentNode.insertBefore(bar, c); }
    getJSON("api/status").then(function (st) {
      bar.textContent = "";
      var txt = !st.claude ? "Claude Code wasn't found on this PC. See LOCAL.md to install it inside WSL."
        : st.error ? st.error
        : st.running ? "Claude is working on the queue (started " + ago(st.startedAt) + ")."
        : st.pauseUntil && st.pauseUntil > Date.now() && st.waiting ? "The last Claude run stopped early (exit " + st.lastExit + ", often a usage limit). It tries again by itself in about " + fmtMin((st.pauseUntil - Date.now()) / 60000) + "."
        : st.waiting ? "Work is waiting. Claude starts on it shortly."
        : "Local studio · Claude is idle" + (st.lastEnd ? " (last run finished " + ago(st.lastEnd) + ")" : "") + ".";
      bar.appendChild(el("span", { text: txt + " " }));
      if (!st.running && st.claude) bar.appendChild(el("button", { class: "btn", type: "button", text: "Run the queue now", onclick: function () {
        fetch("api/run", { method: "POST" }).then(function () { setTimeout(localStatus, 1500); });
      } }));
    }, function () { bar.textContent = "The local studio isn't responding. Is local/start.sh still running in the Ubuntu window?"; });
  }

  /* ---------- render ---------- */
  function renderAll() { renderShorts(); renderLib("chars"); renderLib("scenes"); renderPickers(); }
  function media(id, f) { return f ? "shorts/" + id + "/" + f : ""; }

  function renderShorts() {
    var list = S.shorts.filter(function (s) {
      if (S.chFilter !== "all" && chanOf(s) !== S.chFilter) return false;
      if (S.filter === "needs") return chanOf(s) === "sticky" && stickyState(s) === "needs";
      return S.filter === "all" || (S.filter === "ready" ? s.status === "ready" : s.status !== "ready");
    });
    $("n-shorts").textContent = S.shorts.length || "";
    var ready = S.shorts.filter(function (s) { return s.status === "ready"; }).length;
    var needs = S.shorts.filter(function (s) { return chanOf(s) === "sticky" && stickyState(s) === "needs"; }).length;
    $("shorts-sum").textContent = S.shorts.length ? S.shorts.length + " shorts · " + ready + " ready · " + (S.shorts.length - ready) + " in the queue" + (needs ? " · " + needs + " need your audio" : "") : "Nothing yet. Add a short to start.";
    var box = $("list-shorts"); box.textContent = "";
    if (!list.length) box.appendChild(el("div", { class: "empty", text: "No shorts here." }));
    list.forEach(function (s) { box.appendChild(card(s)); });
  }

  function card(s) {
    if (chanOf(s) === "sticky") return stickyCard(s);
    var vers = s.versions || [], vi = S.ver[s.id] != null ? S.ver[s.id] : vers.length - 1, cur = vers[vi];
    var mon = el("div", { class: "monitor" }, [cur
      ? el("video", { src: media(s.id, cur.video), poster: media(s.id, cur.poster), controls: "", playsinline: "", preload: "none" })
      : el("div", { class: "slate" }, [el("b", { text: s.status === "working" ? (s.progress || 0) + "%" : "—" }), s.status === "working" ? s.stage : "Not made yet"])]);
    var st = s.status || "queued", label = { queued: "Queued", working: "In production", revision: "Revision queued", ready: "Ready", failed: "Failed" }[st] || st;
    var chars = (s.characters || []).map(function (c) { var x = S.chars.filter(function (k) { return k.id === c; })[0]; return x ? x.name : c; });
    var scene = S.scenes.filter(function (k) { return k.id === s.scene; })[0];
    var body = el("div", { class: "body" }, [
      el("div", {}, [el("h2", { text: s.title || s.id }), el("div", { class: "meta" }, [el("span", { class: "chan", text: CHANNELS["deadpan-doug"] }), el("span", { class: "pill " + (st === "failed" ? "revision" : st), text: label }),
        el("span", { text: (s.durationMin || "?") + (s.durationMax && s.durationMax !== s.durationMin ? "–" + s.durationMax : "") + " s" }),
        chars.length ? el("span", { text: chars.join(", ") }) : el("span", { text: "Doug" }),
        scene ? el("span", { text: scene.name }) : s.newScene ? el("span", { text: s.newScene }) : null,
        s.episode ? el("span", { class: "tag", text: s.episode }) : null])]),
      descNode(s)
    ]);
    if (st !== "ready") {
      var idx = Math.max(0, Math.min(STAGES.length - 1, s.stageIndex || 0));
      var eta = st === "working" && s.etaMinutes != null ? "About " + fmtMin(s.etaMinutes - (Date.now() - (s.updatedAt || Date.now())) / 60000) + " left"
        : st === "working" ? "Working" : st === "failed" ? (s.note || "Couldn't be made") : "Waiting for Claude to pick it up. It starts by itself; this can take a few minutes.";
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
  /* ---------- sticky card: writing narration -> needs audio -> making video -> ready ---------- */
  function copyText(t, mid) {
    var done = function () { say(mid, "Narration copied. Paste it into ElevenLabs.", "ok"); };
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(t).then(done, function () { fallbackCopy(t, mid); });
    fallbackCopy(t, mid);
  }
  function fallbackCopy(t, mid) {
    var ta = el("textarea", { style: "position:fixed;top:0;left:0;opacity:0" }); ta.value = t; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); say(mid, "Narration copied. Paste it into ElevenLabs.", "ok"); } catch (e) { say(mid, "Couldn't copy. Select the text and copy it by hand.", "err"); }
    document.body.removeChild(ta);
  }
  function narrBox(s, withButtons) {
    var t = S.narr[s.id] || "", mid = "narr-msg-" + s.id;
    var kids = [el("span", { class: "lab", text: "Narration · " + (t ? t.split(/\s+/).length + " words" : "loading…") }), el("pre", { text: t || "The narration will appear here." })];
    if (withButtons) kids.push(el("div", { class: "row" }, [
      el("button", { class: "btn sticky", type: "button", text: "Copy narration", disabled: t ? null : "", onclick: function () { copyText(t, mid); } }),
      LOCAL ? el("button", { class: "btn", type: "button", text: "Upload narration audio", onclick: function () { uploadLocal(s, mid); } })
        : el("a", { class: "btn", href: "https://github.com/" + OWNER + "/" + REPO + "/upload/" + BRANCH + "/shorts/" + s.id, target: "_blank", rel: "noopener", text: "Upload narration audio" }),
      el("span", { class: "msg", id: mid, role: "status" })]));
    return el("div", { class: "narr" }, kids);
  }
  function reviseBox(s, kind, summary, placeholder, button, okText) {
    var ta = el("textarea", { maxlength: 4000, placeholder: placeholder, "aria-label": summary + " for " + (s.title || s.id) });
    var mid = kind + "-msg-" + s.id, m = el("span", { class: "msg", id: mid, role: "status" });
    return el("details", { class: "revise" }, [el("summary", { text: summary }), ta, el("div", { class: "row" }, [
      el("button", { class: "btn primary", type: "button", text: button, onclick: function () {
        var t = ta.value.trim(); if (t.length < 5) return say(mid, "Describe what should change.", "err");
        var at = Date.now(); propose("shorts/" + s.id + "/revision-" + at + ".json", { text: t, at: at, done: false, kind: kind }, mid, okText);
      } }), m])]);
  }
  function stickyCard(s) {
    var vers = s.versions || [], vi = S.ver[s.id] != null ? S.ver[s.id] : vers.length - 1, cur = vers[vi];
    var ss = stickyState(s);
    var label = { writing: "Writing narration", needs: "Needs audio", "audio-in": "Audio received", video: "Making video", ready: "Ready", failed: "Failed" }[ss] || ss;
    var pill = { writing: "working", needs: "needs", "audio-in": "working", video: "working", ready: "ready", failed: "revision" }[ss] || "queued";
    var slate = { writing: "Writing the narration", needs: "Waiting for your narration audio", "audio-in": "Audio received. The video starts soon", video: s.stage || "Making the video", failed: "Couldn't be made" }[ss] || "";
    var mon = el("div", { class: "monitor" }, [cur
      ? el("video", { src: media(s.id, cur.video), poster: media(s.id, cur.poster), controls: "", playsinline: "", preload: "none" })
      : el("div", { class: "slate" }, [el("b", { text: ss === "video" ? (s.progress || 0) + "%" : ss === "needs" ? "MP3?" : "—" }), slate])]);
    var body = el("div", { class: "body" }, [
      el("div", {}, [el("h2", { text: s.title || s.id }), el("div", { class: "meta" }, [el("span", { class: "chan sticky", text: CHANNELS.sticky }),
        el("span", { class: "pill " + pill, text: label }), cur && cur.seconds ? el("span", { text: cur.seconds + " s" }) : null])]),
      s.description ? el("p", { class: "desc clamp", text: "Notes: " + s.description }) : null
    ]);
    if (ss === "needs") {
      body.appendChild(el("p", { class: "desc", text: "Copy the narration into ElevenLabs, then upload the MP3 into this short's folder and click Commit changes. The video starts by itself." + (s.note ? "\nFact-check notes: " + s.note : "") }));
      body.appendChild(narrBox(s, true));
      body.appendChild(reviseBox(s, "narration", "Rewrite narration", "What should change in the words? e.g. make the hook about the vault door", "Send back for rewriting",
        "GitHub opened in a new tab. Click Commit changes; Claude rewrites the narration."));
    } else if (ss !== "ready") {
      var idx = Math.max(0, Math.min(9, s.stageIndex || 0));
      var eta = ss === "writing" ? (s.status === "working" ? "Researching and writing" : "Waiting for Claude to pick it up. It starts by itself; this can take a few minutes.")
        : ss === "audio-in" ? "Audio received. Claude starts the video within a few minutes."
        : ss === "failed" ? (s.note || "Couldn't be made")
        : s.etaMinutes != null ? "About " + fmtMin(s.etaMinutes - (Date.now() - (s.updatedAt || Date.now())) / 60000) + " left" : "Working";
      body.appendChild(el("div", { class: "strip" }, [
        el("div", { class: "bar", role: "progressbar", "aria-valuemin": 0, "aria-valuemax": 100, "aria-valuenow": s.progress || 0 }, [el("i", { style: "width:" + (s.progress || 0) + "%;background:var(--sticky)" })]),
        el("div", { class: "meta" }, [el("span", { class: "eta", text: eta }), s.updatedAt ? el("span", { text: "Updated " + ago(s.updatedAt) }) : null, s.note && ss !== "failed" ? el("span", { text: s.note }) : null]),
        el("div", { class: "stages" }, STICKY_STAGES.slice(1).map(function (n, i) { return el("span", { class: i + 1 < idx ? "done" : i + 1 === idx && s.status === "working" ? "now" : "", text: n }); }))]));
      if (S.narr[s.id] && ss !== "writing") body.appendChild(el("details", { class: "narr-more" }, [el("summary", { text: "Narration" }), narrBox(s, false)]));
    }
    if (vers.length) {
      var vrow = el("div", { class: "vers" }, [el("span", { class: "tag", text: "VERSIONS" })]);
      vers.forEach(function (v, i) { vrow.appendChild(el("button", { type: "button", "aria-pressed": String(i === vi), text: "v" + v.v, title: v.notes || "", onclick: function () { S.ver[s.id] = i; renderShorts(); } })); });
      if (cur) vrow.appendChild(el("span", { class: "meta", text: (cur.seconds ? cur.seconds + " s · " : "") + (cur.notes || "") }));
      body.appendChild(vrow);
      if (ss === "ready" && S.narr[s.id]) body.appendChild(el("details", { class: "narr-more" }, [el("summary", { text: "Narration" }), narrBox(s, false)]));
    }
    var revs = (s.revisions || []).concat((S.revs[s.id] || []).filter(function (r) { return !(s.revisions || []).some(function (x) { return x.at === r.at; }); }));
    if (revs.length) body.appendChild(el("div", { class: "revs" }, revs.map(function (r) {
      var what = r.kind === "narration" ? "Narration " : "Video ";
      return el("div", { class: "rev" + (r.done ? "" : " open"), text: what + (r.done ? (r.doneIn === "narration" ? "rewritten: " : "done in v" + (r.doneIn || "?") + ": ") : "change requested: ") + r.text });
    })));
    if (vers.length && s.status !== "working") body.appendChild(reviseBox(s, "video", "Request a revision", "What should change in the video? e.g. slower cuts in the middle, bigger map", "Queue revision",
      "GitHub opened in a new tab. Click Commit changes to queue the revision."));
    if (cur) body.appendChild(el("div", { class: "actions" }, [el("a", { class: "btn", href: media(s.id, cur.video), download: slug(s.title) + "_v" + cur.v + ".mp4", text: "Download v" + cur.v })]));
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
  function setChannel(ch) {
    S.channel = ch;
    $("pick-channel").querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.ch === ch)); });
    var sticky = ch === "sticky";
    $("sticky-fields").hidden = !sticky; $("doug-fields").hidden = sticky; $("how-sticky").hidden = !sticky; $("how-doug").hidden = sticky;
    $("sub-new").textContent = sticky ? "Give it a title. Claude researches the story and writes the narration; you voice it in ElevenLabs and upload the MP3; Claude makes the video to fit." : "Describe the bit. Claude writes the timing, builds any missing character or scene, animates, voices, renders and checks it.";
    $("in-title").placeholder = sticky ? "Thieves Broke Into a Diamond Vault Thought to Be Impenetrable — Antwerp diamond heist, 2003" : "When the barista still gets your name wrong";
    say("msg-new", "");
  }
  $("pick-channel").addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (b) setChannel(b.dataset.ch); });
  $("f-new").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var title = $("in-title").value.trim(), desc = $("in-desc").value.trim();
    if (title.length < 3) return say("msg-new", "Give the short a title.", "err");
    if (S.channel === "sticky") {
      var sid = slug(title), sn = 2; while (S.shorts.some(function (s) { return s.id === sid; })) sid = slug(title).slice(0, 44) + "-" + sn++;
      var t0 = Date.now();
      return propose("shorts/" + sid + "/short.json", { id: sid, title: title, channel: "sticky", description: $("in-notes").value.trim(),
        status: "queued", stage: "Queued", stageIndex: 0, progress: 0, etaMinutes: null, note: "", versions: [], revisions: [], createdAt: t0, updatedAt: t0 },
        "msg-new", "GitHub opened in a new tab. Click Commit changes; Claude writes the narration first.");
    }
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
  $("filters-ch").addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (!b) return; S.chFilter = b.dataset.c; $("filters-ch").querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); renderShorts(); });
  $("filters").addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (!b) return; S.filter = b.dataset.f; $("filters").querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); }); renderShorts(); });

  /* ---------- routing ---------- */
  function route() {
    var v = (location.hash || "#shorts").slice(1); if (!$("view-" + v)) v = "shorts";
    document.querySelectorAll(".view").forEach(function (s) { s.hidden = s.id !== "view-" + v; });
    document.querySelectorAll("nav.tabs a").forEach(function (a) { a.setAttribute("aria-current", a.dataset.view === v ? "page" : "false"); });
  }
  window.addEventListener("hashchange", route); route();
  if (LOCAL) {
    var how = function (sel, i, html) { var li = document.querySelectorAll(sel + " li")[i]; if (li) li.innerHTML = html; };
    how("#how-sticky", 0, "<b>Add the title here.</b> It's saved on this PC and Claude starts right away.");
    how("#how-sticky", 3, "<b>Tap Upload narration audio</b> and pick the MP3. Not happy with the words? Use <b>Rewrite narration</b> first.");
    how("#how-doug", 0, "<b>Add it here.</b> It's saved on this PC.");
    how("#how-doug", 1, "<b>Production starts by itself.</b> Claude Code runs on this PC. The bar at the top shows whether it's working; <b>Run the queue now</b> starts it by hand.");
    localStatus(); setInterval(function () { if (document.visibilityState === "visible") localStatus(); }, 15000);
    setInterval(function () { if (document.visibilityState === "visible") load(); }, 30000);
  }
  load();
  setInterval(function () { if (document.visibilityState === "visible" && S.shorts.some(function (s) { return s.status === "working" || s.status === "queued" || (chanOf(s) === "sticky" && stickyState(s) === "audio-in"); })) load(); }, 120000);
})();
