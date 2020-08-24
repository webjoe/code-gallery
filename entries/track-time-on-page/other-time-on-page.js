var _learnq = _learnq || [];
var start = new Date();

window.onbeforeunload = function () {
  var end = new Date();
  _learnq.push([
    "track",
    "Viewed Page",
    {
      url: window.location.href,
      time: end.getTime() - start.getTime(),
    },
  ]);
};
