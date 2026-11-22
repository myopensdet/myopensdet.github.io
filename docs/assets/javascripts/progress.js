/*
 * myOpenSDET: progress tracker.
 *
 * Saved ONLY in this browser (localStorage). Nothing is sent anywhere, there is
 * no account, and clearing the browser's site data removes it.
 *
 * What it does
 * - Lesson pages: a "Mark as done" button at the end ([data-zts-done]).
 * - Every page: links to finished lessons get a check mark (menu, cards, lists).
 * - Learning Path: "X of Y lessons done" under each path ([data-zts-path]).
 * - Skills Matrix: the boxes can be ticked; a summary shows each area and the
 *   next skill to learn ([data-zts-matrix]). Every h2 with ticks is an area.
 * - Section overviews: "X of Y topics done", and when every topic is done, a
 *   short message the reader can edit and share (no pop-ups).
 *
 * Without JavaScript the pages still work; the buttons simply stay hidden.
 */
(function () {
  "use strict";

  var KEY = "zts-progress-v1";

  // ---------------------------------------------------------------- storage

  function load() {
    try {
      var data = JSON.parse(window.localStorage.getItem(KEY) || "{}");
      return { lessons: data.lessons || {}, skills: data.skills || {} };
    } catch (err) {
      return { lessons: {}, skills: {} };
    }
  }

  function save(data) {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(data));
      return true;
    } catch (err) {
      return false; // private window or blocked storage
    }
  }

  // ------------------------------------------------------------------ helpers

  /* A page's address inside the site, e.g. "core-automation/api-testing/". */
  function sitePath(href) {
    var url = new URL(href, window.location.href);
    if (url.origin !== window.location.origin) return null;
    var root = window.__md_scope ? window.__md_scope.pathname : "/";
    var path = url.pathname.replace(/index\.html$/, "");
    return path.indexOf(root) === 0 ? path.slice(root.length) : null;
  }

  /* A short, stable id for a skill, made from its words. */
  function skillId(text) {
    var hash = 5381;
    for (var i = 0; i < text.length; i++) hash = ((hash << 5) + hash + text.charCodeAt(i)) | 0;
    return (hash >>> 0).toString(36);
  }

  function skillText(item) {
    return item.textContent.split(" · ")[0].replace(/\s+/g, " ").trim();
  }

  function announce(root, message) {
    var live = root.querySelector("[data-zts-live]");
    if (live) live.textContent = message;
  }

  // ------------------------------------------------------- lesson: mark done

  function setupDoneButton(data) {
    var button = document.querySelector("[data-zts-done]");
    if (!button) return;
    var path = sitePath(window.location.href);
    var render = function () {
      var done = Boolean(data.lessons[path]);
      button.setAttribute("aria-pressed", String(done));
      button.querySelector("[data-zts-done-label]").textContent = done
        ? "Done! Click to undo"
        : "Mark this lesson as done";
      button.classList.toggle("zts-done--on", done);
    };
    button.hidden = false;
    render();
    button.addEventListener("click", function () {
      if (data.lessons[path]) delete data.lessons[path];
      else data.lessons[path] = new Date().toISOString().slice(0, 10);
      var saved = save(data);
      render();
      markLinks(data);
      var note = document.querySelector("[data-zts-done-note]");
      if (note) {
        note.textContent = !saved
          ? "Your browser is blocking saving, so this will be forgotten when you leave."
          : data.lessons[path]
            ? "Saved in this browser only. Well done!"
            : "Unmarked.";
      }
    });
  }

  // --------------------------------------------- check marks on lesson links

  function markLinks(data) {
    var here = sitePath(window.location.href);
    var links = document.querySelectorAll(".md-content a[href], .md-nav__link[href]");
    links.forEach(function (link) {
      if (link.closest("[data-zts-matrix-panel]")) return;
      var path = sitePath(link.getAttribute("href"));
      // On the lesson itself, only the menu entry gets the check mark (not the
      // headings in "On this page" or the breadcrumb).
      if (path === here && !link.closest(".md-nav--primary")) path = null;
      var done = path !== null && path !== "" && Boolean(data.lessons[path]);
      link.classList.toggle("zts-is-done", done);
    });
    document.querySelectorAll("[data-zts-path]").forEach(function (note) {
      // The lessons are in the list or table just before this note.
      // Tables sit inside a scroll wrapper, so look inside each element too.
      var list = note.previousElementSibling;
      while (list && ["OL", "UL", "TABLE"].indexOf(list.tagName) === -1) {
        var inner = list.querySelector("table");
        if (inner) {
          list = inner;
          break;
        }
        list = list.previousElementSibling;
      }
      if (!list) return;
      var lessons = list.querySelectorAll("a[href]");
      var finished = Array.prototype.filter.call(lessons, function (a) {
        return Boolean(data.lessons[sitePath(a.getAttribute("href"))]);
      }).length;
      note.hidden = false;
      note.innerHTML =
        '<span class="zts-meter" aria-hidden="true"><span style="inline-size:' +
        Math.round((finished / Math.max(1, lessons.length)) * 100) +
        '%"></span></span> Your progress: <strong>' +
        finished + " of " + lessons.length + "</strong> lessons done";
    });
  }

  // --------------------------------------------------------- skills matrix

  function setupMatrix(data) {
    var panel = document.querySelector("[data-zts-matrix]");
    if (!panel) return;
    var article = panel.closest("article") || document.querySelector(".md-content__inner");
    var levels = [];
    var current = null;
    article.querySelectorAll("h2, .task-list-item").forEach(function (node) {
      if (node.tagName === "H2") {
        var name = node.textContent.replace("¶", "").trim();
        current = { name: name, heading: node, items: [] };
        levels.push(current);
      } else if (current) {
        current.items.push(node);
      }
    });

    levels = levels.filter(function (level) { return level.items.length > 0; });

    levels.forEach(function (level) {
      level.items.forEach(function (item) {
        var input = item.querySelector("input[type=checkbox]");
        if (!input) return;
        var text = skillText(item);
        var id = skillId(text);
        input.disabled = false;
        input.checked = Boolean(data.skills[id]);
        input.setAttribute("aria-label", text);
        input.addEventListener("change", function () {
          if (input.checked) data.skills[id] = 1;
          else delete data.skills[id];
          var saved = save(data);
          renderMatrix(panel, levels, data);
          announce(panel, saved ? "Saved." : "Your browser is blocking saving.");
        });
      });
      var meter = document.createElement("p");
      meter.className = "zts-level-meter";
      meter.setAttribute("data-zts-level-meter", "");
      level.heading.insertAdjacentElement("afterend", meter);
      level.meter = meter;
    });

    panel.hidden = false;
    panel.querySelector("[data-zts-reset]").addEventListener("click", function () {
      if (!window.confirm("Clear every tick on the Skills Matrix? This cannot be undone.")) return;
      data.skills = {};
      save(data);
      levels.forEach(function (level) {
        level.items.forEach(function (item) {
          var input = item.querySelector("input[type=checkbox]");
          if (input) input.checked = false;
        });
      });
      renderMatrix(panel, levels, data);
      announce(panel, "All ticks cleared.");
    });
    renderMatrix(panel, levels, data);
  }

  function renderMatrix(panel, levels, data) {
    var rows = [];
    var next = null;
    var total = 0;
    var ticked = 0;
    levels.forEach(function (level) {
      var done = level.items.filter(function (item) {
        var input = item.querySelector("input[type=checkbox]");
        if (!input) return false;
        if (!input.checked && !next) next = item;
        return input.checked;
      }).length;
      total += level.items.length;
      ticked += done;
      var percent = Math.round((done / Math.max(1, level.items.length)) * 100);
      var short = level.name.replace(/\s*\(.*\)$/, "");
      level.meter.innerHTML =
        '<span class="zts-meter" aria-hidden="true"><span style="inline-size:' + percent +
        '%"></span></span> ' + done + " of " + level.items.length + " skills";
      rows.push(
        '<li><a href="#' + level.heading.id + '">' + short + "</a>" +
        '<span class="zts-meter" aria-hidden="true"><span style="inline-size:' + percent +
        '%"></span></span><span class="zts-matrix__count">' + done + " of " +
        level.items.length + "</span></li>"
      );
    });
    panel.querySelector("[data-zts-levels]").innerHTML = rows.join("");
    panel.querySelector("[data-zts-total]").textContent = ticked + " of " + total;
    var nextBox = panel.querySelector("[data-zts-next]");
    if (next) {
      var link = next.querySelector("a[href]");
      nextBox.innerHTML =
        "<strong>Your next skill:</strong> " + escapeHtml(skillText(next)) +
        (link ? ' <a href="' + link.getAttribute("href") + '">Learn it: ' +
          escapeHtml(link.textContent) + "</a>" : "");
    } else {
      nextBox.innerHTML = "<strong>Every box is ticked.</strong> You have the full SDET skill set!";
    }
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // ------------------------------------------- section overview: share it

  var REPO = "https://github.com/arshaduzzaman-sm/myopensdet";

  function setupSection(data) {
    var cards = document.querySelectorAll(".zts-topics > ul > li > p:first-child a[href]");
    if (!cards.length) return;
    var old = document.querySelector("[data-zts-section-progress]");
    if (old) old.remove();
    var done = Array.prototype.filter.call(cards, function (a) {
      return Boolean(data.lessons[sitePath(a.getAttribute("href"))]);
    }).length;
    if (done === 0) return;

    var heading = document.querySelector(".md-content__inner h1");
    var section = heading ? heading.textContent.replace("¶", "").trim() : "this section";
    var canonical = document.querySelector('link[rel="canonical"]');
    var url = canonical ? canonical.href : window.location.href;
    var box = document.createElement("div");
    box.setAttribute("data-zts-section-progress", "");
    var meter =
      '<span class="zts-meter" aria-hidden="true"><span style="inline-size:' +
      Math.round((done / cards.length) * 100) + '%"></span></span>';

    if (done < cards.length) {
      box.className = "zts-section-progress";
      box.innerHTML = "<p>" + meter + " You have finished <strong>" + done + " of " +
        cards.length + "</strong> topics in " + escapeHtml(section) + ".</p>";
    } else {
      box.className = "zts-section-progress zts-section-progress--complete";
      var message = "I just finished the " + section + " section of myOpenSDET, " +
        "a free course for becoming an SDET. " + url;
      box.innerHTML =
        "<p><strong>You finished every topic in " + escapeHtml(section) + ". Well done!</strong></p>" +
        '<label for="zts-share-message">Want to share it? Change the message if you like:</label>' +
        '<textarea id="zts-share-message" rows="3"></textarea>' +
        '<p class="zts-section-progress__actions">' +
        '<button type="button" class="md-button" data-act="copy">Copy message</button>' +
        '<a class="md-button" data-act="linkedin" target="_blank" rel="noopener noreferrer">LinkedIn</a>' +
        '<a class="md-button" data-act="x" target="_blank" rel="noopener noreferrer">X</a>' +
        '<a class="md-button" data-act="whatsapp" target="_blank" rel="noopener noreferrer">WhatsApp</a>' +
        "</p>" +
        '<p class="zts-section-progress__star">If this site helped you, a star on ' +
        '<a href="' + REPO + '" target="_blank" rel="noopener">GitHub</a> helps other testers find it.</p>' +
        '<p class="md-visually-hidden" role="status" data-zts-live></p>';
      var text = box.querySelector("textarea");
      text.value = message;
      var links = function () {
        var value = encodeURIComponent(text.value);
        box.querySelector('[data-act="linkedin"]').href =
          "https://www.linkedin.com/sharing/share-offsite/?url=" + encodeURIComponent(url);
        box.querySelector('[data-act="x"]').href = "https://x.com/intent/post?text=" + value;
        box.querySelector('[data-act="whatsapp"]').href = "https://wa.me/?text=" + value;
      };
      text.addEventListener("input", links);
      links();
      // LinkedIn only takes the address, so copy the message for pasting.
      box.querySelector('[data-act="linkedin"]').addEventListener("click", function () {
        if (navigator.clipboard) {
          navigator.clipboard.writeText(text.value).then(function () {
            announce(box, "Message copied. Paste it into your LinkedIn post.");
          });
        }
      });
      box.querySelector('[data-act="copy"]').addEventListener("click", function () {
        if (!navigator.clipboard) return announce(box, "Select the text and copy it.");
        navigator.clipboard.writeText(text.value).then(function () {
          announce(box, "Message copied. Paste it into your post.");
        });
      });
    }
    var first = document.querySelector(".md-content__inner .zts-topics");
    var anchor = first && first.previousElementSibling && first.previousElementSibling.tagName === "H2"
      ? first.previousElementSibling
      : first;
    anchor.insertAdjacentElement("beforebegin", box);
  }

  // ------------------------------------------------------------------- start

  function run() {
    var data = load();
    setupDoneButton(data);
    setupMatrix(data);
    markLinks(data);
    setupSection(data);
  }

  // The site swaps pages without a full reload (instant navigation), so run on
  // every page the theme shows. Fall back to a plain load if that is missing.
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(run);
  } else {
    document.addEventListener("DOMContentLoaded", run);
  }
})();
