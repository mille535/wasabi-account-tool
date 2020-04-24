# Nothing to see here

This is my first foray into programming. I am learning Python using Kirk Byers Python for Network Engineers free course. There really isn't anything of use to anybody here. I am merely just a n00b trying to learn something new. The only thing anybody may find here are a *ton* of spelling errors and poorly constructed code. Sorry it's not something more interesting just using git to keep my PCs in sync. 


Script to automate to creation and deletetion of Wasabi users, policies, and buckets
for use with MSP360 backup.

Notes:
  * AWS API Credentials must be stored in .aws folder in root of user profile

ToDo:
  * Convert policy document creation function that uses JSON module insted of a string
  * Add report to show users and policies applied
  * Error checking. make sure account dont already exist and handle error, input checking as well
  * Maybe in the future have an option for verbosity to show output of response for each command
  * Unrelated to this but find a way to test if buckets are secure

Issues:
  * ARN name in remove portion of the script is hardcoded making this code not portable
  * Group removal is also hardcoded
  * writing to desktop does not work under unix
