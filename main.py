# Kirk Miller April 2020

import os
from os import system, name
import boto3


def provision_account(customer):
    """This function provisions a new Wasabi account with var customer"""
    clear()
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
    print("Operation complete. Program Exiting.")

    # writes displayed text to a file on the desktop
    with open(out_key_file, "w") as f:
        f.write(out_file_text)

    # uncomment the line below for compiled verion
    input("Press Enter to exit...")


def remove_account(customer):
    """This function removes a Wasabi account with var customer"""
    # Create IAM client, %userprofile%\.aws needs to contain config and
    # credentials files
    client = boto3.client('iam',
                          endpoint_url='https://iam.wasabisys.com'
                          )

    # creates s3 client for which we will create a bucket with
    s3 = boto3.client('s3',
                      endpoint_url='https://s3.wasabisys.com',
                      )

    # creates variable for policy document name based on client name
    policy_name = customer + "-limit"
    limit_arn_name = "arn:aws:iam::100000045798:policy/" + policy_name

    # removes user from backupclients group
    response = client.remove_user_from_group(
        GroupName='backupclients',
        UserName=customer
    )
    print("Remove user: {} from group: backupclients.....Done".format(customer))

    # remove user from policy
    response = client.detach_user_policy(
        UserName=customer,
        PolicyArn=limit_arn_name
    )
    print(
        "Detach policy: {} from user: {}.....Done".format(
            limit_arn_name,
            customer))

    # Remove limit policy
    response = client.delete_policy(
        PolicyArn=limit_arn_name
    )
    print("Deleting IAM policy: {}.....Done".format(limit_arn_name))

    # remove access keys for user
    response = client.list_access_keys(
        UserName=customer,
    )

    for i in response.get('AccessKeyMetadata'):
        response = client.delete_access_key(
            UserName=customer,
            AccessKeyId=i.get('AccessKeyId')
        )
    print("Deleting Key and Secret for user: {}.....Done".format(customer))

    # Remove user account
    response = client.delete_user(
        UserName=customer
    )
    print("Remove IAM user {}.....Done".format(customer))

    # remove data and bucket
    response = s3.list_objects_v2(
        Bucket=customer,
    )

    while response['KeyCount'] > 0:
        print('Deleting {} objects from bucket {}'.format(
            (len(response['Contents'])), customer))
        response = s3.delete_objects(
            Bucket=customer,
            Delete={
                'Objects': [{'Key': obj['Key']} for obj in response['Contents']]
            }
        )
        response = s3.list_objects_v2(
            Bucket=customer,
        )

    print('Now deleting bucket {}'.format(customer))
    response = s3.delete_bucket(
        Bucket=customer
    )
    print("Deleting bucket: {}.....Done".format(customer))
    print("Account for {} has been sucesfully removed.\n".format(customer))
    print("Program Exiting.")

    # uncomment the line below for compiles verion
    input("Press Enter to exit...")

# function to clear the screen buffer


def clear():
    """clears the terminal window"""
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def cli_setup():
    """main cli setup loop"""
    clear()
    print("-" * 79)
    print('|{:^77}|'.format("Wasabi Client Setup Tool"))
    print('|{:77}|'.format("-" * 77))
    print('|{:<77}|'.format("1. Setup a new customer."))
    print('|{:77}|'.format(" " * 77))
    print('|{:<77}|'.format("2. Delete an existing customer."))
    print('|{:77}|'.format(" " * 77))
    print('|{:<77}|'.format(
        "3. This DOS looking box gives me anxiety. Exit the program."))
    print("-" * 79)

    answer = None
    while answer not in ("1", "2", "3"):
        answer = input("Please selection an option: ")
        if answer == "1":
            clear()
            print("-" * 79)
            print('|{:^77}|'.format(
                "Wasabi Client Setup Tool - New Account Setup"))
            print('|{:77}|'.format("-" * 77))
            print('|{:77}|'.format(" " * 77))
            print('|{:77}|'.format(" " * 77))
            print('|{:<77}|'.format(
                "A new Wasabi account comprises of three main items: A bucket, a user, and a"))
            print('|{:<77}|'.format(
                "limiting policy. These items will be programmatically derived from the input"))
            print('|{:<77}|'.format(
                "below. The user and the bucket will have the same name as the customer name"))
            print('|{:<77}|'.format(
                "and the policy will be the customers name appended with -limit. "))
            print('|{:77}|'.format(" " * 77))
            print('|{:<77}|'.format(
                "If you would like to exit at this point user CTL+C"))
            print('|{:77}|'.format(" " * 77))
            print('|{:77}|'.format(" " * 77))
            print("-" * 79)
            customer_name = input("Enter the customers name: ")
            provision_account(customer_name)
        elif answer == "2":
            clear()
            print("-" * 79)
            print('|{:^77}|'.format("Wasabi Client Setup Tool - Remove Account"))
            print('|{:77}|'.format("-" * 77))
            print('|{:77}|'.format(" " * 77))
            print('|{:77}|'.format(" " * 77))
            print('|{:<77}|'.format(
                "The remove account function should only be used on accounts setup with this"))
            print('|{:<77}|'.format(
                "tool as incosisencies in naming conventions on account setup manually will"))
            print('|{:<77}|'.format(
                "raise an error leaving accounts still partially setup. Should this happen the"))
            print('|{:<77}|'.format(
                "user, bucket, and policy can all be removed manually at"))
            print('|{:<77}|'.format("https://console.wasabisys.com"))
            print('|{:77}|'.format(" " * 77))
            print('|{:<77}|'.format(
                "If you would like to exit at this point user CTL+C"))
            print('|{:77}|'.format(" " * 77))
            print('|{:77}|'.format(" " * 77))
            print("-" * 79)
            customer_name = input("Enter the customers name: ")
            remove_account(customer_name)
        elif answer == "3":
            print("Exiting Program.")
            break
        else:
            print("Invalid selection, please enter 1,2,3")


cli_setup()
