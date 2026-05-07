// Mobile nav toggle + simple form spam honeypot init.
(function () {
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open);
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  // Touch dropdown support: tap parent to expand, tap again to follow.
  document.querySelectorAll(".site-nav__has-children > a").forEach((a) => {
    let expanded = false;
    a.addEventListener("click", (e) => {
      if (window.innerWidth > 1100) return;
      if (!expanded && a.getAttribute("href") !== "#") {
        e.preventDefault();
        expanded = true;
        const sub = a.nextElementSibling;
        if (sub) sub.style.display = "block";
      }
    });
  });
})();
