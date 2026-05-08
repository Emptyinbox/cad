// Auto-collapse FAQ sections inside .prose--rich [data-faq] articles.
// Finds H2 headings whose text matches /faq/i, then converts following H3+content
// into <details> elements until the next H2.
(function () {
  const articles = document.querySelectorAll(".prose--rich[data-faq]");
  articles.forEach((article) => {
    const children = Array.from(article.children);
    let inFaq = false;
    let i = 0;
    while (i < children.length) {
      const el = children[i];
      if (el.tagName === "H2") {
        const txt = (el.textContent || "").toLowerCase();
        inFaq = /\bfaqs?\b|frequently\s+asked/i.test(txt);
        if (inFaq) el.setAttribute("data-faq-h2", "");
        i++;
        continue;
      }
      if (inFaq && el.tagName === "H3") {
        // Collect siblings until the next H2 or H3
        const collected = [];
        let j = i + 1;
        while (j < children.length && !/^H[23]$/.test(children[j].tagName)) {
          collected.push(children[j]);
          j++;
        }
        // Build <details>
        const details = document.createElement("details");
        details.setAttribute("data-faq-q", "");
        const summary = document.createElement("summary");
        summary.textContent = el.textContent;
        details.appendChild(summary);
        const body = document.createElement("div");
        body.className = "faq-body";
        collected.forEach((c) => body.appendChild(c));
        details.appendChild(body);
        // Replace the H3 with the details, removing collected nodes
        el.replaceWith(details);
        i = j; // skip past collected (their position in `children` reflects original DOM)
        // children array stale now — rebuild on next iteration loop
        const rebuilt = Array.from(article.children);
        children.length = 0; children.push(...rebuilt);
        i = rebuilt.indexOf(details) + 1;
        continue;
      }
      i++;
    }
  });
})();

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
