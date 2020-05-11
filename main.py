"""
Kirk Miller April 2020.

A simple command line tool to
add or remove wasabi storage accounts using Amazon's boto3
library and the S3 API
"""

import os
import argparse
import boto3


def provision_account(customer):
    """This function provisions a new Wasabi account with var customer"""
    # Create IAM client, %userprofile%\.aws needs to contain config and
    # credentials files
    client = boto3.client('iam',
                          endpoint_url='https://iam.wasabisys.com'
                          )

    # creates s3 client for which we will create a bucket with
    s3 = boto3.client('s3',
                      endpoint_url='https://s3.wasabisys.com',
                      )

    # create a bucket using the customers name:
    s3.create_bucket(Bucket=customer)
    print("Creating bucket: {}.....Done".format(customer))

    # creates variable for policy document name based on client name
    policy_name = customer + "-limit"

    # policy document stored as string with two variables for clients name
    policy_document = """{{
    "Version": "2012-10-17",
    "Statement": [
      {{
        "Effect": "Allow",
        "Action": "s3:ListAllMyBuckets",
        "Resource": "arn:aws:s3:::*"
      }},
     {{
        "Effect": "Allow",
        "Action": "s3:*",
        "Resource": [
          "arn:aws:s3:::{0}",
          "arn:aws:s3:::{0}/*"
        ]
      }}
    ]
  }}
  """
    # create a new IAM policy using the policy_name and policy_document string
    response = client.create_policy(
        PolicyName=policy_name,
        PolicyDocument=policy_document.format(customer)
    )
    print("Creating IAM policy: {}.....Done".format(policy_name))

    # newly created policy arn name into variable
    policy_arn = response.get('Policy').get('Arn')

    # Create new IAM user
    response = client.create_user(
        UserName=customer
    )
    print("Creating IAM user: {}.....Done".format(customer))

    # Attach new IAM policy to new IAM user
    response = client.attach_user_policy(
        UserName=customer,
        PolicyArn=policy_arn
    )
    print(
        "Attaching policy: {} to user: {}.....Done".format(
            policy_name,
            customer))

    # Adds newly created user to backupclients group
    response = client.add_user_to_group(
        GroupName='backupclients',
        UserName=customer
    )
    print("Adding user: {} to group: backupclients.....Done".format(customer))

    # Create API key for new user
    response = client.create_access_key(
        UserName=customer
    )
    print("Requisting Key and Secret for user: {}.....Done".format(customer))

    # Store key and secret in variable
    customer_access_key = response.get('AccessKey').get('AccessKeyId')
    customer_secret_key = response.get('AccessKey').get('SecretAccessKey')

    # Some output text to be displaed and saved off to file
    out_file_text = """Wasabi Key and Secret for {}:
  Access Key: {}
  Secret Key: {}

  * Please document this key pair in Wasabi clientinfo Excel file.
  * Do not publish these keys online and store them in a safe place.

  You may input this information to setup the customer in MSP360
  """.format(customer, customer_access_key, customer_secret_key)

    # Sets the file name and path as a vairable
    out_key_file = os.path.join(
        os.path.join(
            os.path.expanduser('~')),
        customer +
        '-WasabiKey.txt')

    # display new user key/secret pair
    print("-" * 80)
    print(out_file_text)
    print("-" * 80)
    print("A copy of key/secret pair for {} has been saved to {}".format(customer, out_key_file))
    print("Account for {} added successfully.".format(customer))

    # writes displayed text to a file on the desktop
    with open(out_key_file, "w") as f:
        f.write(out_file_text)


def remove_account(customer):
    """This function removes a Wasabi account with var customer. It has been
    re-written to take the dictionary input from the get_user_into function"""
    # Create IAM client, %userprofile%\.aws needs to contain config and
    # credentials files
    client = boto3.client('iam',
                          endpoint_url='https://iam.wasabisys.com'
                          )

    # creates s3 client for which we will create a bucket with
    s3 = boto3.client('s3',
                      endpoint_url='https://s3.wasabisys.com',
                      )

    # removes user all groups
    for g in customer['GroupList']:
        response = client.remove_user_from_group(
            GroupName=g,
            UserName=customer['Username']
        )
        print(
            "Remove user: {} from group: {}.....Done".format(
                customer['Username'], g))

    # remove user from all polies
    for p in customer['PolicyList']:
        response = client.detach_user_policy(
            UserName=customer['Username'],
            PolicyArn=p
        )
        print(
            "Detach policy: {} from user: {}.....Done".format(
                p,
                customer['Username']))

    # delete limit policy
    for p in customer['PolicyList']:
        response = client.delete_policy(
            PolicyArn=p
        )
        print("Deleting IAM policy: {}.....Done".format(p))

    # remove access keys for user
    for k in customer['AccessKey']:
        response = client.delete_access_key(
            UserName=customer['Username'],
            AccessKeyId=k)
    print(
        "Deleting Key: {} for user: {}.....Done".format(
            k, customer['Username']))

    # Remove user account
    response = client.delete_user(
        UserName=customer['Username']
    )
    print("Remove IAM user {}.....Done".format(customer['Username']))

    # remove data and bucket
    response = s3.list_objects_v2(
        Bucket=customer['Username'],
    )

    while response['KeyCount'] > 0:
        print('Deleting {} objects from bucket {}'.format(
            (len(response['Contents'])), customer['Username']))
        response = s3.delete_objects(
            Bucket=customer['Username'],
            Delete={
                'Objects': [{'Key': obj['Key']} for obj in response['Contents']]
            }
        )
        response = s3.list_objects_v2(
            Bucket=customer['Username'],
        )

    print('Now deleting bucket {}'.format(customer['Username']))
    response = s3.delete_bucket(
        Bucket=customer['Username']
    )
    print("Deleting bucket: {}.....Done".format(customer['Username']))
    print("Account for {} removed successfully.".format(customer['Username']))


def user_exist(customer):
    """This fucntion will return a bool based on if a users exists"""
    client = boto3.client('iam',
                          endpoint_url='https://iam.wasabisys.com'
                          )

    try:
        exist = client.get_user(UserName=customer)
    except client.exceptions.NoSuchEntityException as e:
        exist = False
    return bool(exist)


def get_user_info(customer):
    """Gets key account information and stores it as a dict"""

    # setup variables
    user_data = {'Username': customer}
    group_list = []
    policy_list = []
    access_keys = []

    # setup boto3 client for Wasabi
    client = boto3.client('iam',
                          endpoint_url='https://iam.wasabisys.com',
                          )

    # lists all groups attached to specified users
    response = client.list_groups_for_user(
        UserName=customer
    )

    # stores group info as a list in user group dict
    for group in response['Groups']:
        group_list.append(group['GroupName'])
        user_data['GroupList'] = group_list

    # lists all policies attached to specified user
    response = client.list_attached_user_policies(
        UserName=customer
    )

    # stores policy info as a list in user group dict
    for policy in response['AttachedPolicies']:
        policy_list.append(policy['PolicyArn'])
        user_data['PolicyList'] = policy_list

    # lists all access keys for specified user
    response = client.list_access_keys(
        UserName=customer,
    )

    # stores access key info as a list in user group dict
    for access_key in response.get('AccessKeyMetadata'):
        access_keys.append(access_key['AccessKeyId'])
        user_data['AccessKey'] = access_keys
    return user_data


# Create the argument parser
my_parser = argparse.ArgumentParser(description='Wasabi user maintenance tool',
                                    epilog="2020 Kirk Miller, enjoy :)")
my_group = my_parser.add_mutually_exclusive_group(required=True)

# Add the arguments
my_group.add_argument('-a',
                      '--add',
                      metavar='username',
                      type=str,
                      help='Create a new Wasabi user')
my_group.add_argument('-d',
                      '--delete',
                      metavar='username',
                      type=str,
                      help='Delete an existing Wasabi user')

# Execute parse_args()
args = my_parser.parse_args()

# file path for .aws folder
creds_file = os.path.join(
    os.path.join(
        os.path.expanduser('~')),
    '.aws')

# main logic loop for command line arguments
if args.add and os.path.isdir(creds_file):
    if not user_exist(args.add):
        provision_account(args.add)
    else:
        print("Account already exists, please check name")
elif args.delete and os.path.isdir(creds_file):
    if user_exist(args.delete):
        print("Are you sure you want to remove user: {}?".format(args.delete))
        cust_name = input("To confirm enter the user name again: ")
        if args.delete == cust_name:
            remove_account(get_user_info(args.delete))
        else:
            print("ERROR: Names do not match.")
    else:
        print("User doesn't exist please check spelling")
else:
    print("ERROR: Could not find Wasabi credentials file.")
    print("Please make sure the {} folder is present and"
          " contains config and credentials files".format(creds_file))
