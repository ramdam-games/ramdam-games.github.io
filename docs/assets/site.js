(() => {
  const box = document.querySelector(".lightbox");
  const shots = [...document.querySelectorAll(".gallery .shot")];
  if (box && shots.length && typeof box.showModal === "function") {
    const img = box.querySelector("img");
    const cap = box.querySelector("figcaption");
    let index = 0;
    const show = (i) => {
      index = (i + shots.length) % shots.length;
      img.src = shots[index].href;
      img.alt = shots[index].dataset.caption || "";
      cap.textContent = shots[index].dataset.caption || "";
    };
    shots.forEach((a, i) => a.addEventListener("click", (ev) => {
      ev.preventDefault();
      show(i);
      box.showModal();
    }));
    box.querySelector(".lb-close").addEventListener("click", () => box.close());
    box.querySelector(".lb-prev").addEventListener("click", () => show(index - 1));
    box.querySelector(".lb-next").addEventListener("click", () => show(index + 1));
    box.addEventListener("click", (ev) => { if (ev.target === box) box.close(); });
    box.addEventListener("keydown", (ev) => {
      if (ev.key === "ArrowLeft") show(index - 1);
      if (ev.key === "ArrowRight") show(index + 1);
    });
  }

  const chips = [...document.querySelectorAll(".chip")];
  const entries = [...document.querySelectorAll(".entries.all .entry")];
  chips.forEach((chip) => chip.addEventListener("click", () => {
    chips.forEach((c) => c.classList.toggle("on", c === chip));
    const want = chip.dataset.filter;
    entries.forEach((en) => en.classList.toggle("hidden", want !== "all" && en.dataset.game !== want));
  }));
})();
