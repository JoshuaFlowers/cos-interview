This program uses a flask server to authenticate users and search for recent emails. It utilized the Authlib library for authorization and account access using OAuth2.0.

To add a new authentication partner, create a new adapter which implements the authorize and search_emails methods, then add it to the list of adapters in the server with the appropriate domain mapping.

Authorization is achieved using the /connect/email route, passing an email address in the 'email' query param.

Utilize the /emails/search endpoint by passing an epoch timestamp from which to search. Return will be a string representing a boolean, either True or False, indicating whether or not any emails have been received since the supplied timestamp. 


This application was designed with each partner having their own adapter which extends a BaseAdapter. Here are the steps to add a new partner:
 	1. Add the necessary credentials to the environment via the .env file
	2. Create a new adapter implementing the search_emails function
	3. import the new adapter in server.py
	4. Add the appropriate mapping to the 'adapters' dictionary

Further customization can be achieved using custom success endpoints for each partner. However, that is not needed at this point and as such a common endpoint is being used for redirecting the user after the oauth flow.

The Authlib library has been implemented in order to utilize features and take advantage of continuous development being done without having to maintain them ourselves. Using this library enables for future feature development. While the Authlib library is convenient, it does come with a learning curve for those unfamiliar with them, perhaps moreso than using REST apis. Additionally, the use of a library comes with things happening under the hood that require further dives into the docs or code base in order to fully understand what is happening at each step. Implementing the OAuth2.0 specs from scratch would potentially make the developer more familiar with what was taking place, but would come at the added cost of having to maintain that codebase and leave open the possibilities of introducing bugs and security holes. 

The use of sessions has been implemented to store user data temporarily. For a more complete solution, a database would be used for persistent storage including the refresh token which is recommended to be kept in longterm storage.
