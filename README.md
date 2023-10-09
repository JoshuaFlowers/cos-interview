This program uses a flask server to authenticate users and search for recent emails. It utilized the Authlib library for authorization and account access using OAuth2.0.

To add a new authentication partner, create a new adapter which implements the authorize and search_emails methods, then add it to the list of adapters in the server with the appropriate domain mapping.

Authorization is achieved using the /connect/email route, passing an email address in the 'email' query param.

Utilize the /emails/search endpoint by passing an epoch timestamp from which to search. Return will be a string representing a boolean, either True or False, indicating whether or not any emails have been received since the supplied timestamp. 
