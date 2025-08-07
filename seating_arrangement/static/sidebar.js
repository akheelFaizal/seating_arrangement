document.addEventListener("DOMContentLoaded", () => {
  const sidebarButtons = document.querySelectorAll(".sidebar-btn");

  sidebarButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      sidebarButtons.forEach((b) => b.classList.remove("active"));

      btn.classList.add("active");
    });
  });
});
