
$(document).ready(function () {
  //  Background image slide into animation (Slide in from the right and fade in)
  $(".hero-bg").css({ right: "-100%", left: "auto", opacity: 0 }).animate(
    { right: "0%", opacity: 1 },
    1500,
    "swing"
  );

  // delay 1.2s
  setTimeout(function () {
    $(".hero-content").css({ left: "-50px", opacity: 0, position: "relative" }).animate(
      { left: "0", opacity: 1 },
      1000
    );
  }, 1200);


  setTimeout(function () {
    $(".hero-content .btn-primary").fadeTo(4000, 1);
  }, 1600);
});
 var typed = new Typed('#typed-text', {
    strings: [
      "CITS5505 - Group25",
    ],
    typeSpeed: 40,
    backSpeed: 20,
    backDelay: 1500,
    startDelay: 300,
    fadeOut: true,
    smartBackspace: false,
    loop: true
  });