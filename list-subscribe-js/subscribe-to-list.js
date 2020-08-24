function sendKlaviyoSubscribe(kl_list_id, kl_email, kl_signup_source) {
  var _learnq = _learnq || [];
  // send Identify request to cookie the browser
  _learnq.push(["identify", { $email: kl_email }]);
  var xhr = new XMLHttpRequest();
  var url = "https://manage.kmail-lists.com/ajax/subscriptions/subscribe";
  // assemble the form data for the request
  var params = `g=${kl_list_id}&email=${encodeURIComponent(
    kl_email
  )}&$fields=$source&$source=${kl_signup_source}`;
  // open the request
  xhr.open("POST", url, true);
  // add the headers to the request
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhr.setRequestHeader("cache-control", "no-cache");
  // log response when request completes
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      console.log(xhr.responseText);
    }
  };
  // send request with form data
  xhr.send(params);
}
