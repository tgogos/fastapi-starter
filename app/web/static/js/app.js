/**
 * Minimal vanilla JS bindings for the HTMX UI.
 * - Confirm before destructive HTMX deletes
 * - Dismiss flash messages
 * - Send CSRF header on HTMX requests when meta csrf-token is present
 */
(function () {
  "use strict";

  document.body.addEventListener("click", function (event) {
    var dismiss = event.target.closest(".flash-dismiss");
    if (dismiss) {
      var flash = dismiss.closest(".flash");
      if (flash) {
        flash.remove();
      }
      return;
    }

    var deleteBtn = event.target.closest(".js-confirm-delete");
    if (deleteBtn) {
      var message = deleteBtn.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(message)) {
        event.preventDefault();
        event.stopPropagation();
      }
    }
  });

  document.body.addEventListener("htmx:configRequest", function (event) {
    var meta = document.querySelector('meta[name="csrf-token"]');
    if (!meta) {
      return;
    }
    var token = meta.getAttribute("content");
    if (token && !event.detail.headers["X-CSRF-Token"]) {
      event.detail.headers["X-CSRF-Token"] = token;
    }
  });
})();
