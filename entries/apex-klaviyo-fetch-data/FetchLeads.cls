Http http = new Http();
HttpRequest request = new HttpRequest();
public DateTime NOW = datetime.now();
public Long LAST_24 = NOW.addDays(-1).getTime();
request.setEndpoint('https://a.klaviyo.com/api/v1/metric/H7hJPA/timeline?api_key=pk_ff3901982a4b1467a2d52291d757e4b362&since=' + LAST_24);
request.setMethod('GET');
HttpResponse response = http.send(request);

// If the request is successful, parse the JSON response.
if (response.getStatusCode() == 200) {

    //Deserialize the JSON string into collections of primitive data types.
    Map<String, Object> results = (Map<String, Object>) JSON.deserializeUntyped(response.getBody());

    //Cast the values in the 'results' key as a list
    List<Object> profiles = (List<Object>) results.get('data');

    for(Object profile: profiles){
        Map<String,Object> profileData = (Map<String,Object>)profile;
        Map<String,Object> person = (Map<String,Object>)(profileData.get('person'));

        //Get the Lead if it exists already in SF
        List<Lead> existingLeads = new list<Lead>();
        existingLeads = [SELECT Id FROM Lead WHERE Email = :person.get('$email').toString()];

        //Return early if the Lead already exists
        if (existingLeads.size() > 0) {
            return;
        }

        //Otherwise, create a new one
        Lead newLead = new Lead();
        newLead.LastName = person.get('$last_name');
        newLead.FirstName = person.get('$first_name');
        newLead.Company = person.get('$organization').toString().length() > 0 ? person.get('$organization').toString() : 'Not Provided';
        newLead.Email = person.get('$email').toString();
        newLead.Country = person.get('$country').toString();
        newLead.City = person.get('$city').toString();
        newLead.Phone = person.get('$phone_number').toString();
        newLead.Title = person.get('$title').toString();

        insert(newLead);
    }
}