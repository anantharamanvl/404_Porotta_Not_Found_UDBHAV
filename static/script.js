// static/script.js
document.addEventListener("DOMContentLoaded", function () {
  // Update the total-count badge if present
  const totalEl = document.getElementById("total-count");
  if (totalEl) {
    // get number from template (already set server-side) - no change needed
  }

  // confirm download actions
  document.querySelectorAll('a[href*="/download_report"]').forEach(a => {
    a.addEventListener('click', function (ev) {
      // optional: confirm download
      // ev.preventDefault(); if you want to intercept
    });
  });

  // Make form submit with keyboard 'Enter' friendly
  const genForm = document.getElementById("gen-form");
  if (genForm) {
    genForm.addEventListener("submit", function () {
      // small visual feedback could be added here
    });
  }
});
