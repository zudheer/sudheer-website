(function () {
  var nav = document.querySelector(".nav");
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");

  window.addEventListener("scroll", function () {
    nav.classList.toggle("is-scrolled", window.scrollY > 8);
  });

  if (toggle) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); });
    });
  }

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12 }
  );
  document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });
})();
