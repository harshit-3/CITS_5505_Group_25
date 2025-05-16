
document.addEventListener("DOMContentLoaded", () => {
  const dropdown = document.querySelector('.nav-item.dropdown');

  if (dropdown) {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');

    dropdown.addEventListener('mouseenter', () => {
      menu.classList.add('show');
      toggle.setAttribute('aria-expanded', 'true');
    });

    dropdown.addEventListener('mouseleave', () => {
      menu.classList.remove('show');
      toggle.setAttribute('aria-expanded', 'false');
    });
  }
});



document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            alert.classList.add('fade');
        }, 2000);
    });
});
