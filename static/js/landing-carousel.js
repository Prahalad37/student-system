/**
 * Roadmap carousel – vanilla JS, no dependencies
 */
(function () {
  const slides = document.querySelectorAll('.roadmap-slide');
  const dots = document.querySelectorAll('.roadmap-dot');

  if (!slides.length || !dots.length) return;

  function goToSlide(index) {
    const i = Math.max(0, Math.min(index, slides.length - 1));
    slides.forEach(function (s, idx) {
      s.classList.toggle('active', idx === i);
    });
    dots.forEach(function (d, idx) {
      d.classList.toggle('active', idx === i);
    });
  }

  dots.forEach(function (dot, idx) {
    dot.addEventListener('click', function () {
      goToSlide(idx);
    });
  });

  // Optional: auto-advance every 6 seconds
  let interval = setInterval(function () {
    const activeIdx = Array.from(slides).findIndex(function (s) {
      return s.classList.contains('active');
    });
    goToSlide((activeIdx + 1) % slides.length);
  }, 6000);

  // Pause on hover
  const carousel = document.querySelector('.roadmap-carousel');
  if (carousel) {
    carousel.addEventListener('mouseenter', function () {
      clearInterval(interval);
    });
    carousel.addEventListener('mouseleave', function () {
      interval = setInterval(function () {
        const activeIdx = Array.from(slides).findIndex(function (s) {
          return s.classList.contains('active');
        });
        goToSlide((activeIdx + 1) % slides.length);
      }, 6000);
    });
  }
})();

/**
 * Hero sticker carousel – one sticker at a time, auto-slide
 */
(function () {
  const heroSlides = document.querySelectorAll('.hero-sticker-slide');
  if (!heroSlides.length) return;

  function goToHeroSlide(index) {
    const i = Math.max(0, Math.min(index, heroSlides.length - 1));
    heroSlides.forEach(function (s, idx) {
      s.classList.toggle('active', idx === i);
    });
  }

  setInterval(function () {
    const activeIdx = Array.from(heroSlides).findIndex(function (s) {
      return s.classList.contains('active');
    });
    goToHeroSlide((activeIdx + 1) % heroSlides.length);
  }, 4500);
})();
