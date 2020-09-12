@isTest
private class ApexKlaviyoAPITest {
    /**
     * Runs a series of mock Apex-Klaviyo Track/Identify requests
     */
    private class SingleRequestMock implements HttpCalloutMock {
        /** Create a mock for HTTP responses from callouts. */
        public HTTPResponse respond(HTTPRequest req) {
            HTTPResponse res = new HTTPResponse();
            res.setBody('{}');
            res.setStatusCode(200);
            return res;
        }
    }
    /** Tests the ApexKlaviyoAPI APEX class. */
    static testMethod void testApexKlaviyoAPI() {
        // Start test
        Test.startTest();
        Test.setMock(HttpCalloutMock.class, new SingleRequestMock());
        // Add the Klaviyo public API key for your live or testing account
        String publicKey = 'PUBLIC API KEY HERE';
        // Add a Salesforce Account record ID (that has associated Contact records)
        // that you'd like to use for this test
        ApexKlaviyoAPI updateJob = new ApexKlaviyoAPI('001d0000022PcT9AAK');
        Integer timestamp = Datetime.now().getTime().intValue() / 1000;
        String event = 'Apex Klaviyo API Wrapper Test Event';
        Map < String, Object > customerProperties = new Map < String, Object > ();
        Map < String, Object > properties = new Map < String, Object > ();
        /** Test that the ApexKlaviyoAPI class's identify method works. */
        updateJob.identify(publicKey, customerProperties);
        System.enqueueJob(updateJob);
        /** Test that the ApexKlaviyoAPI class's track method works with
            all params. */
        updateJob.track(publicKey, event, customerProperties, properties, timestamp);
        System.enqueueJob(updateJob);
        /** Test that the ApexKlaviyoAPI class's track method works with
            just api key, event name, customer properties, and event properties. */
        updateJob.track(publicKey, event, customerProperties, properties);
        System.enqueueJob(updateJob);
        /** Test that the ApexKlaviyoAPI class's track method works with
            just api key, event name, customer properties, and timestamp. */
        updateJob.track(publicKey, event, customerProperties, timestamp);
        System.enqueueJob(updateJob);
        /** Test that the ApexKlaviyoAPI class's track method works with
            just api key, event name, and customer properties. */
        updateJob.track(publicKey, event, customerProperties);
        System.enqueueJob(updateJob);
        Test.stopTest();
    }
}
