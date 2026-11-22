/*
 * myOpenSDET: "Copy link" and the phone "Share" button (share.js).
 * The LinkedIn, X and WhatsApp buttons are plain links and need no script.
 * Nothing here talks to any other website.
 */
(function () {
  "use strict";

  function setup() {
    document.querySelectorAll("[data-zts-copy]").forEach(function (button) {
      if (!navigator.clipboard) return; // stays hidden
      button.hidden = false;
      var label = button.querySelector("[data-zts-copy-label]");
      button.addEventListener("click", function () {
        navigator.clipboard.writeText(button.getAttribute("data-zts-copy")).then(
          function () {
            label.textContent = "Link copied";
            button.classList.add("zts-share__btn--done");
            window.setTimeout(function () {
              label.textContent = "Copy link";
              button.classList.remove("zts-share__btn--done");
            }, 2000);
          },
          function () {
            label.textContent = "Could not copy";
          }
        );
      });
    });

    // Phones and some browsers have their own share sheet.
    document.querySelectorAll("[data-zts-native-share]").forEach(function (button) {
      if (typeof navigator.share !== "function") return; // stays hidden
      button.hidden = false;
      button.addEventListener("click", function () {
        navigator
          .share({
            title: button.getAttribute("data-title"),
            url: button.getAttribute("data-zts-native-share"),
          })
          .catch(function () {
            /* the reader closed the share sheet: nothing to do */
          });
      });
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(setup);
  } else {
    document.addEventListener("DOMContentLoaded", setup);
  }
})();
