var lang = window.location.href.split("country=");

if (lang == "uk") {
  lang = "United Kingdom";
} else if (lang == "fr") {
  lang = "Europe";
} else if (lang == "AU") {
  lang = "Australia";
} else if (lang == "DE") {
  lang = "Europe";
} else if (lang == "US") {
  lang = "United States";
} else if (lang == "GB") {
  lang = "United Kingdom";
} else {
  lang = "Europe";
}
var _learnq = _learnq || [];
_learnq.push([
  "identify",
  {
    "Store View": lang,
  },
]);
