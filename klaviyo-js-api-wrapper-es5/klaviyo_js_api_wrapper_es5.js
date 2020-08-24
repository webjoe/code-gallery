function KLJS(token, email) {
  /**
   * Usage:
   *  Initialize Klaviyo Tracking object using
   *    klonsite = new KLJS('123abc','person@email.com')
   * Inputs:
   *  token (String) = Public API key for Klaviyo account
   *  email (String) = email address of the current browser
   */
  this.token = token;
  this.email = email;
}
KLJS.prototype.encode = function (jsonData) {
  return encodeURI(btoa(JSON.stringify(jsonData)));
};
KLJS.prototype.makeRequest = function (url) {
  var xhr = new XMLHttpRequest();
  // open the request
  xhr.open("GET", url, true);
  // log response when request completes
  xhr.onreadystatechange = function () {
    if (xhr.readyState == 4 && xhr.status == 200) {
      console.log(xhr.responseText);
    }
  };
  // send request with form data
  xhr.send();
};
KLJS.prototype.track = function (eventName, eventProps) {
  /**
   * Usage:
   *  Track events to Klaviyo using
   *    klonsite.track('Climbed Tree',{'Type':'Redwood'})
   * Inputs:
   *  eventName (String) = name of the event to track
   *  eventProp (JSON) = properties of the event to track
   */
  var customerProperties = {};
  customerProperties["$email"] = this.email;
  eventProps["$is_session_activity"] = true;
  // build payload
  var jsonData = {
    token: this.token,
    event: eventName,
    customer_properties: customerProperties,
    properties: eventProps,
  };
  this.makeRequest(
    "https://a.klaviyo.com/api/track?data=" + this.encode(jsonData)
  );
};
KLJS.prototype.identify = function (customerProperties) {
  if (customerProperties.hasOwnProperty("$email")) {
    this.email = customerProperties["$email"];
  }
  customerProperties["$email"] = this.email;
  var jsonData = {
    token: this.token,
    properties: customerProperties,
  };
  this.makeRequest(
    "https://a.klaviyo.com/api/identify?data=" + this.encode(jsonData)
  );
};
