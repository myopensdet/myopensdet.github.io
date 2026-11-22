/*
  myOpenSDET: the "Was this page helpful?" buttons at the end of a lesson.

  A click only shows the thank-you note on the page. Nothing is sent
  anywhere: the site has no analytics and no tracking.
  The form itself is in overrides/partials/feedback.html.
*/
(function () {
  "use strict";

  function setup() {
    var form = document.forms.feedback;
    if (!form || form.dataset.ztsReady) return;
    form.dataset.ztsReady = "1";
    form.querySelectorAll("[type=submit]").forEach(function (button) {
      button.addEventListener("click", function (event) {
        event.preventDefault();
        var value = button.getAttribute("data-md-value");
        form.firstElementChild.disabled = true;
        form.classList.add("zts-feedback--done");
        button.classList.add("zts-feedback__chosen");
        var note = form.querySelector(".md-feedback__note [data-md-value='" + value + "']");
        if (note) note.hidden = false;
      });
    });
    form.hidden = false;
  }

  // The site swaps pages without a full reload (instant navigation), so run on
  // every page the theme shows. Fall back to a plain load if that is missing.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(setup);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
  } else {
    setup();
  }
})();
