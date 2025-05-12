$(document).ready(function () {
  // Animate hero background fade in
  $(".hero-bg").css({ opacity: 0 }).animate({ opacity: 1 }, 1500);

  // Animate hero content fade + slide in
  setTimeout(function () {
    $(".hero-content").css({ opacity: 0, position: "relative", top: "40px" }).animate(
      { top: "0", opacity: 1 },
      1000
    );
  }, 1000);

  // Show button fade-in
  setTimeout(function () {
    $(".hero-content .btn-primary").fadeTo(1500, 1);
  }, 1600);
});

// Typed.js initialization
var typed = new Typed('#typed-text', {
  strings: ["CITS5505 - Group25", "Track. Analyze. Thrive."],
  typeSpeed: 40,
  backSpeed: 20,
  backDelay: 2000,
  startDelay: 300,
  loop: true,
  fadeOut: true,
  smartBackspace: false
});
