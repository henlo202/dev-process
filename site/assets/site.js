// Small progressive enhancements: mobile menu, nav filter, tier filter, copy buttons.
(function () {
  var body = document.body;
  var menu = document.querySelector(".menu");
  if (menu) menu.addEventListener("click", function () {
    var open = body.classList.toggle("nav-open");
    menu.setAttribute("aria-expanded", open ? "true" : "false");
  });

  var filter = document.querySelector(".filter");
  if (filter) filter.addEventListener("input", function () {
    var q = filter.value.trim().toLowerCase();
    document.querySelectorAll(".side li").forEach(function (li) {
      li.style.display = !q || li.textContent.toLowerCase().indexOf(q) !== -1 ? "" : "none";
    });
    document.querySelectorAll(".nav-sec").forEach(function (d) { if (q) d.open = true; });
  });

  // Keep the current page's nav section open.
  var cur = document.querySelector('.side a[aria-current="page"]');
  if (cur) {
    var sec = cur.closest("details");
    if (sec) sec.open = true;
  }

  document.querySelectorAll(".tier-filter button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tier = btn.getAttribute("data-tier");
      document.querySelectorAll(".tier-filter button").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      document.querySelectorAll(".flow .step[data-tiers]").forEach(function (s) {
        var applies = tier === "all" || s.getAttribute("data-tiers").split(" ").indexOf(tier) !== -1;
        s.classList.toggle("dim", !applies);
      });
    });
  });

  document.querySelectorAll(".copy").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var code = btn.parentElement.querySelector("code");
      if (!code || !navigator.clipboard) return;
      navigator.clipboard.writeText(code.textContent).then(function () {
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = "Copy"; }, 1500);
      });
    });
  });
})();
