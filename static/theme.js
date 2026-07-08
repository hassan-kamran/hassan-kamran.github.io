/* Loaded synchronously in <head> so a stored dark-theme choice applies
   before first paint. Light is the default for everyone else. */
(() => {
  "use strict";
  try {
    if (localStorage.getItem("theme") === "dark") {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  } catch (e) { /* private mode etc. — stay on the light default */ }
})();
