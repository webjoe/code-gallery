window.addEventListener("klaviyoForms", function (e) {
  // Note: This is expected to trigger only for known profiles
  // Does not trigger when an embedded form is served, e.g. to avoid firing for forms in footer on every page.
  // Example output:  "Klaviyo Form - submit"
  if (e.detail.type != "embedOpen") {
    var formAction = String(e.detail.type);
    _learnq.push([
      "track",
      "Klaviyo Form - ".concat(formAction),
      Object.assign({}, e.detail.metaData),
    ]);
  }
});
