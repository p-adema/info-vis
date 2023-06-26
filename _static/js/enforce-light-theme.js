function enforceLightMode() {
  // Remove theme switcher, disallowing dark mode.
  const switchButton = document.querySelector('.theme-switch-button');
  if (typeof switchButton !== 'undefined') {
    switchButton.remove();
  }

  // Enforce light mode, because that is when our story looks the best :)
  if (localStorage.getItem('theme') !== 'light') {
    localStorage.setItem('mode', 'light');
    localStorage.setItem('theme', 'light');
    window.location.reload();
  }
}

window.addEventListener('load', enforceLightMode);
