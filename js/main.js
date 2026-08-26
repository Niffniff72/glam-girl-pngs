// Glam Girl PNGs — site interactions & animations

document.addEventListener("DOMContentLoaded", () => {
  /* Sparkle field in the hero */
  const field = document.querySelector(".sparkle-field");
  if (field) {
    const count = window.innerWidth < 720 ? 18 : 34;
    for (let i = 0; i < count; i++) {
      const s = document.createElement("span");
      s.className = "sparkle";
      s.style.left = Math.random() * 100 + "%";
      s.style.top = Math.random() * 100 + "%";
      s.style.animationDelay = (Math.random() * 3.2).toFixed(2) + "s";
      s.style.animationDuration = (2.4 + Math.random() * 2.4).toFixed(2) + "s";
      const size = 3 + Math.random() * 4;
      s.style.width = size + "px";
      s.style.height = size + "px";
      field.appendChild(s);
    }
  }

  /* Nav shrink + mobile toggle */
  const nav = document.querySelector(".nav");
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");

  const onScroll = () => {
    if (!nav) return;
    nav.classList.toggle("scrolled", window.scrollY > 40);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  if (toggle && links) {
    toggle.addEventListener("click", () => links.classList.toggle("open"));
    links.querySelectorAll("a").forEach((a) =>
      a.addEventListener("click", () => links.classList.remove("open"))
    );
  }

  /* Scroll reveal */
  const revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealEls.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in-view"));
  }

  /* Email opt-in confetti burst (front-end only — wire the form action up to Brevo) */
  const optinForm = document.querySelector(".optin-form");
  if (optinForm) {
    optinForm.addEventListener("submit", (e) => {
      const burst = document.querySelector(".confetti-burst");
      if (!burst) return;
      e.preventDefault();
      burst.innerHTML = "";
      const colors = ["#ff2f92", "#ffd77a", "#e8b64b", "#ff8dc7"];
      for (let i = 0; i < 26; i++) {
        const p = document.createElement("span");
        const size = 5 + Math.random() * 6;
        p.style.position = "absolute";
        p.style.left = 50 + (Math.random() * 60 - 30) + "%";
        p.style.top = "45%";
        p.style.width = size + "px";
        p.style.height = size + "px";
        p.style.borderRadius = Math.random() > 0.5 ? "50%" : "2px";
        p.style.background = colors[i % colors.length];
        p.style.opacity = "0";
        p.style.transition = "transform 1s ease-out, opacity 1s ease-out";
        burst.appendChild(p);
        requestAnimationFrame(() => {
          const angle = Math.random() * Math.PI * 2;
          const dist = 80 + Math.random() * 140;
          p.style.transform = `translate(${Math.cos(angle) * dist}px, ${Math.sin(angle) * dist - 40}px) rotate(${Math.random() * 360}deg)`;
          p.style.opacity = "1";
        });
        setTimeout(() => { p.style.opacity = "0"; }, 700);
      }
      const btn = optinForm.querySelector("button");
      if (btn) {
        const original = btn.textContent;
        btn.textContent = "You're In! ✨";
        setTimeout(() => { btn.textContent = original; optinForm.reset(); }, 2200);
      }
    });
  }
});
