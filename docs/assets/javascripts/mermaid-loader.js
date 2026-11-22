/*
  myOpenSDET: draw diagrams with our own copy of Mermaid, never a CDN.

  Without this file, the theme downloads Mermaid from unpkg.com on pages with
  diagrams, at whatever 12.x version is newest that day, and every reader's
  browser contacts that server. This file stops both:

  - It sets a small stand-in `window.mermaid` before the theme's script runs.
    The theme sees that Mermaid "exists" and doesn't fetch it from unpkg.com.
  - The real file (vendor/, pinned below) is loaded only when a page actually
    draws a diagram, so pages without diagrams don't download 5 MB.
  - The browser checks the file's SHA-384 hash (Subresource Integrity) and
    refuses to run it if even one byte changed.

  The theme only calls mermaid.initialize(config) and mermaid.render(id, text).
  Works with instant navigation: the stand-in stays in place between pages.

  To update Mermaid: see CONTRIBUTING.md, "Updating Mermaid".
  scripts/check_built_site.py checks the hash below matches the file.
*/
(function () {
  "use strict";

  var VERSION = "12.2.0";
  var INTEGRITY = "sha384-8xUhuLNMjW/cI2Dacg3DR4WliYznvIg0LVG1stctThKD/YVrJFI9TNCFxft5NYgp";

  if (window.mermaid) {
    return;
  }

  var src = new URL("vendor/mermaid-" + VERSION + ".min.js", document.currentScript.src).href;
  var settings = null;
  var loading = null;

  function load() {
    if (!loading) {
      loading = new Promise(function (resolve, reject) {
        var script = document.createElement("script");
        script.src = src;
        script.integrity = INTEGRITY;
        script.onload = function () {
          // The real file has replaced window.mermaid with itself.
          if (settings) {
            window.mermaid.initialize(settings);
          }
          resolve(window.mermaid);
        };
        script.onerror = function () {
          loading = null;
          reject(new Error("Could not load " + src));
        };
        document.head.appendChild(script);
      });
    }
    return loading;
  }

  window.mermaid = {
    initialize: function (config) {
      settings = config;
    },
    render: function (id, text) {
      return load().then(function (real) {
        return real.render(id, text);
      });
    },
  };
})();
