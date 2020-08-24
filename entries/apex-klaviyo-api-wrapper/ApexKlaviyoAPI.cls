public class ApexKlaviyoAPI implements Queueable,Database.AllowsCallouts {
    /**
     * Handle any Account record-related Track and Identify calls originating from Apex triggers
     */
    static String ENDPOINT = 'https://a.klaviyo.com/api/';
    private String path = '';
    private String method = '';
    private List<String> payloads = new List<String>();
    private List<Contact> contacts = new List<Contact>();

    // Construct API request object by gathering the Contacts associated with the given Account
    public ApexKlaviyoAPI(String accountId) {
      this.contacts = [SELECT Email FROM Contact where Account.Id = :accountId];
    }

    // Lock the timestamp to "now"
    public Integer lockTimestamp() {
        Datetime dt = Datetime.now();
        return dt.getTime().intValue() / 1000;
    }

    // Base64 and URL encode parameters for request
    public String buildQueryString(Map < String, Object > params) {
        String jsonString = JSON.serialize(params);
        Blob jsonBlob = Blob.valueOf(jsonString);
        String b64String = EncodingUtil.base64Encode(jsonBlob);
        return EncodingUtil.urlEncode(b64String, 'UTF-8');
    }

    // Make a request to the specified Klaviyo API path
    public void execute(QueueableContext context) {
      HttpRequest request = new HttpRequest();
      request.setEndpoint(ApexKlaviyoAPI.ENDPOINT);
      String baseEndpoint = request.getEndpoint() + this.path;
      request.setMethod(this.method);
      request.setTimeout(5000);

      HTTP http;
      HTTPResponse res;
      for (String payload : this.payloads) {
          if (this.path == 'track' || this.path == 'identify') {
              request.setEndpoint(baseEndpoint + '?data=' + payload);
          } else {
              System.debug('Only Track and Identify have been implemented so far!');
          }

          http = new HTTP();
          try {
              res = http.send(request);
              System.debug(res.toString());
          } catch (System.CalloutException e) {
              System.debug('ERROR:' + e);
          }
      }
    }

    // Build Identify payload
    public void identify(String publicKey, Map < String, Object > properties) {
        this.path = 'identify';
        this.method = 'GET';
        Map < String, Object > params = new Map < String, Object > ();
        params.put('token', publicKey);
        for (Contact contact : contacts) {
            properties.put('email', contact.get('Email'));
            params.put('properties', properties);
            this.payloads.add(buildQueryString(params));
        }
    }

    // Build Track payload if track is sent with only an event name and email
    public void track(String publicKey, String event, Map < String, Object > customerProperties) {
      track(publicKey, event, customerProperties, new Map < String, Object > ());
    }

    // Build Track payload if track is sent with only an event name and email and timestamp
    public void track(String publicKey, String event, Map < String, Object > customerProperties, Integer timestamp) {
      track(publicKey, event, customerProperties, new Map < String, Object > (), timestamp);
    }

    // Build Track payload if track is sent without a timestamp, lock it to now
    public void track(String publicKey, String event, Map < String, Object > customerProperties, Map < String, Object > properties) {
      track(publicKey, event, customerProperties, properties, lockTimestamp());
    }

    // Build Track payload if all parameters are sent
    public void track(String publicKey, String event, Map < String, Object > customerProperties, Map < String, Object > properties, Integer timestamp) {
        this.path = 'track';
        this.method = 'GET';
        Map < String, Object > params = new Map < String, Object > ();
        params.put('token', publicKey);
        params.put('token', publicKey);
        params.put('event', event);
        params.put('time', timestamp);
        params.put('properties', properties);
        for (Contact contact : contacts) {
            customerProperties.put('email', contact.get('Email'));
            params.put('customer_properties', customerProperties);
            this.payloads.add(buildQueryString(params));
        }
    }
}
