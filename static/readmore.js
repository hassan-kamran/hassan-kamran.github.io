document.addEventListener("DOMContentLoaded", function () {
  // Set up Read More functionality for long testimonials
  document.querySelectorAll(".long-testimonial").forEach((card) => {
    const readMoreBtn = card.querySelector(".read-more-btn");

    readMoreBtn.addEventListener("click", function () {
      if (card.classList.contains("expanded")) {
        // Collapse
        card.classList.remove("expanded");
        this.textContent = "Read More";

        // Scroll back to top of card for better UX
        card.scrollIntoView({ behavior: "smooth", block: "nearest" });
      } else {
        // Expand
        card.classList.add("expanded");
        this.textContent = "Read Less";
      }
    });
  });
});
