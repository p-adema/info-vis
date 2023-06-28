(($, window, document) => {

  $(window).load(function() {
    // Remove theme switcher, disallowing dark mode.
    const switchButton = $('.theme-switch-button');
    if (switchButton.length > 0) {
      switchButton.remove();
    }

    // Enforce light mode, because that is when our story looks the best :)
    if ($('html').attr('data-theme') !== 'light') {
      // Switch theme right now.
      $('html').attr('data-theme', 'light');

      // Set light mode to be permanent for future visits.
      localStorage.setItem('mode', 'light');
      localStorage.setItem('theme', 'light');
    }
  });

})(jQuery, window, document);
