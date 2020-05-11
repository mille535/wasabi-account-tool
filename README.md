# Wasabi S3 Account Creation Tool for MSP360

## Warning
This is my first independent Python program created 100% by myself without guidance from a book or online course. This has mostly been a learning exercise for me but had blossomed into a tool that actually works. I intend to keep iterating the more that I learn, so long as my interest in this project stays high and time allows.  That being said this script works for me and my environment but hasn't been tested on other systems and use-cases, YMMV.

## Application Description
This script will provision a user on Wasabi (or s3 if properly modified). Provisioning a user consists of: creating a bucket, creating an IAM user, creating and applying an IAM policy, adding user to backupclients group, and generating key/secret pair.

### Current Work:
  * Check if user exists and setup a dictionary of user attributes. 
    * 2 separate functions: ~~one to check user existence~~ and one to get user details
  * Function to add/change/delete/and test aws credentials

### ToDo:
  * Error checking. make sure account don’t already exist and handle error, input checking as well
  * Convert policy document creation function that uses JSON module instead of a string
  * A way to add / remove credentials stored in .aws folder
    * A way to encrypt saved credentials
  * Add report to show users and policies applied
  * Maybe in the future have an option for verbosity to show output of response for each command
  * ~~ability to run the script completely by command. python main.py -add -joe~~
  * ~~A better interface whether its a better console interface or just command line or web--just something less clunky~~

### Issues:
  * ARN name in remove portion of the script is hardcoded making this code not portable
  * Group removal is also hardcoded
  * ~~writing to desktop does not work under unix~~ Fixed by using ~ instead of USERPROFILE and taking desktop out of the equation
