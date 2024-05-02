let show_rows = localStorage.getItem("show_rows");
if (show_rows == null) {
  localStorage.setItem("show_rows", 1);
  show_rows = 1;
}
const toggler_title = { 1: "Скрыть", "-1": "Показать" };
const rows = Array.from(document.querySelector("table>tbody").children);
const toggler = document.querySelector(".toggler");

if (show_rows == -1) {
  flip();
}

function flip() {
  toggler.innerText = toggler_title[show_rows];
  rows.forEach((e, index) => {
    if (e.children[0].innerText.trim() !== "1") {
      e.classList.toggle("hidden");
    }
  });
}

toggler.addEventListener("click", () => {
  show_rows = show_rows * -1;
  localStorage.setItem("show_rows", show_rows);
  flip();
});
