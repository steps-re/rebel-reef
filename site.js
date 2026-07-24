/* Rebel Reef site helpers: table CSV export, figure PNG download, click-to-zoom lightbox.
   Progressive enhancement, everything still renders/reads without JS. */
(function () {
  "use strict";

  /* ---------- Tables -> CSV download ---------- */
  function csvEsc(s) {
    s = (s == null ? "" : String(s)).replace(/\s+/g, " ").trim();
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function tableToCSV(tbl) {
    var rows = [];
    tbl.querySelectorAll("tr").forEach(function (tr) {
      var cells = [].slice.call(tr.querySelectorAll("th,td")).map(function (c) {
        return csvEsc(c.innerText);
      });
      if (cells.length) rows.push(cells.join(","));
    });
    return rows.join("\r\n");
  }
  function slug(s) {
    return (s || "table").toLowerCase().replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "").slice(0, 60) || "table";
  }
  function download(name, blob) {
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = name;
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 100);
  }
  document.querySelectorAll("table.data").forEach(function (tbl, i) {
    var cap = tbl.querySelector("caption");
    var title = cap ? cap.textContent : "table-" + (i + 1);
    var tools = document.createElement("div");
    tools.className = "tbltools";
    var btn = document.createElement("button");
    btn.className = "dlbtn";
    btn.type = "button";
    btn.textContent = "⤓ CSV";
    btn.title = "Download this table as CSV";
    btn.addEventListener("click", function () {
      download(slug(title.split(".")[0]) + ".csv",
        new Blob([tableToCSV(tbl)], { type: "text/csv;charset=utf-8;" }));
    });
    tools.appendChild(btn);
    var wrap = tbl.parentElement;
    var anchor = (wrap && wrap.style && wrap.style.overflowX) ? wrap : tbl;
    anchor.parentNode.insertBefore(tools, anchor);
  });

  /* ---------- Lightbox (click figure to zoom) ---------- */
  var box = null;
  function ensureBox() {
    if (box) return box;
    box = document.createElement("div");
    box.className = "lightbox";
    box.innerHTML =
      '<div class="lb-inner"><button class="lb-close" aria-label="Close">×</button>' +
      '<img alt=""><div class="lb-cap"></div></div>';
    box.addEventListener("click", function (e) {
      if (e.target === box || e.target.className === "lb-close") closeBox();
    });
    document.body.appendChild(box);
    return box;
  }
  function openBox(src, cap) {
    ensureBox();
    box.querySelector("img").src = src;
    box.querySelector(".lb-cap").textContent = cap || "";
    box.classList.add("on");
    document.body.style.overflow = "hidden";
  }
  function closeBox() {
    if (box) { box.classList.remove("on"); document.body.style.overflow = ""; }
  }
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeBox();
  });

  /* ---------- Figures: zoom + PNG download ---------- */
  document.querySelectorAll("figure.fig").forEach(function (fig) {
    var img = fig.querySelector("img");
    if (!img) return;
    var cap = fig.querySelector("figcaption");
    var capText = cap ? cap.textContent : (img.alt || "");
    img.classList.add("zoomable");
    img.title = "Click to zoom";
    img.addEventListener("click", function () { openBox(img.src, capText); });
    if (cap) {
      var a = document.createElement("a");
      a.className = "dl";
      a.href = img.getAttribute("src");
      a.setAttribute("download", "");
      a.textContent = "⤓ PNG";
      a.title = "Download this figure";
      cap.appendChild(document.createTextNode(" "));
      cap.appendChild(a);
    }
  });
})();
