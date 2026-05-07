// Mobile nav toggle + tap-to-expand for dropdowns on touch devices.
(function () {
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open);
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      document.body.style.overflow = open ? "hidden" : "";
    });
  }

  // Touch-friendly dropdowns on narrow viewports
  document.querySelectorAll(".site-nav__has-children > a").forEach((a) => {
    let expanded = false;
    a.addEventListener("click", (e) => {
      if (window.innerWidth > 1100) return;
      const sub = a.nextElementSibling;
      if (!expanded && a.getAttribute("href") !== "#") {
        e.preventDefault();
        expanded = true;
        if (sub) sub.style.display = "block";
      }
    });
  });

  // Close mobile nav on link click
  document.querySelectorAll(".site-nav__list a").forEach((link) => {
    link.addEventListener("click", () => {
      if (window.innerWidth <= 1100 && nav.classList.contains("is-open")) {
        // only close if it's not a parent dropdown trigger
        if (!link.parentElement.classList.contains("site-nav__has-children") || link.getAttribute("href") !== "#") {
          nav.classList.remove("is-open");
          toggle && toggle.setAttribute("aria-expanded", "false");
          document.body.style.overflow = "";
        }
      }
    });
  });
})();
