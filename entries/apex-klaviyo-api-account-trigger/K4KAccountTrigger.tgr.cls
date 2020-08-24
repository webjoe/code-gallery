trigger K4KAccountTrigger on Account (after insert, after update) {
    /**
     * If an Account's 'Account Manager', MRR, segment, sales status,
       onboarding specialist, or became customer date changes, send an identify
       request to each contact's Klaviyo profile
     */
    // Add the Klaviyo public API key for your account
    String publicKey = '9BX3wh';
    // Set fields to watch for changes
    List<String> fields = new list<String> {
      'SUPPORT_Account_Manager__c',
      'FM_Total_MRR_of_Parent_Account__c',
      'Revenue_Segment__c',
      'Target_Account_Status__c',
      'Onboarding_Specialist__c',
      'Became_Customer_Date__c'
    };
    for (Account account: Trigger.new) { // Handle bulk inserts
        if (Trigger.isUpdate){
          for (String field: fields) { // Check each watched field
            if (Trigger.oldMap.get(account.Id).get(field) == account.get(field)){
              continue; // no change recorded for this field, ignore
            }
          }
        }
        // Handle any field resolution

        // get CSM email (or other account manager email)
        String csmId = account.SUPPORT_Account_Manager__c;
        String csmEmail;
        if (csmId == null) {
            csmEmail = '';
        } else {
            List<User> users = [SELECT Email FROM User where Id = :csmId LIMIT 1];
            csmEmail = users.get(0).Email;
        }
        // get onboarding specialist email
        String obsId = account.Onboarding_Specialist__c;
        String obsEmail;
        if (obsId == null) {
            obsEmail = '';
        } else {
            List<User> users = [SELECT Email FROM User where Id = :obsId LIMIT 1];
            obsEmail = users.get(0).Email;
        }

        // Set profile properties to send
        Map < String, Object > properties = new Map < String, Object > ();
        properties.put('K4KMRR', account.FM_Total_MRR_of_Parent_Account__c);
        properties.put('K4KManagedBy', csmEmail);
        properties.put('K4KOBS', obsEmail);
        properties.put('K4KCustomerSegment', account.Revenue_Segment__c);
        properties.put('K4KSalesStatus', account.Target_Account_Status__c);
        properties.put('K4KBecameCustomerDate', account.Became_Customer_Date__c);

        // Create queueable job to send profile properties for each contact of triggering account
        ApexKlaviyoAPI updateJob = new ApexKlaviyoAPI(account.Id);
        updateJob.identify(publicKey,properties);
        ID jobID = System.enqueueJob(updateJob);
        System.debug('Queued new job with jobID' + jobID);

    }
}
