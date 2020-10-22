# Sync Squarespace Orders with Salesforce Opportunities

This is a simple python script that will retrieve new Squarespace orders and create corresponding Opportunties in Salesforce.  In addition, if the email address associated with the order does not exist in Salesforce, it will create a new Contact (and corresponding account) for that the person.

Required env vars are externalized, and include a required RecordTypeId for new Opportunties and Contacts.  

Some fields are not sync'd, and multiple order line items are collapsed into a single opportunity (a future update could add support for opportunity line items).

This app is design to be run on a scheduled basis (ie a Heroku dyno w/Heroku Scheduler)
