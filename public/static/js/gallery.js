(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".gallery-item[data-detail-url]").forEach(function (item) {
      item.addEventListener("click", function (event) {
        if (event.target.closest("a, button")) return;
        window.location.href = item.dataset.detailUrl;
      });
    });
  });
})();
