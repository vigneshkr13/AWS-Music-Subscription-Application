# Importing the required librarires
import boto3    
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key 
import json

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')  


def lambda_handler(event, context):
    type = event.get('type')
    email = event.get('email')
    password = event.get('password')
    user_name = event.get('username')
    query_info = event.get('query_info')
    title = event.get('title')
    artist = event.get('artist')
    year = event.get('year')
    
    # Different functionalities are called depending upon the request type.
    if type == "login":
        return handle_login(email, password)
    elif type == "register":
        return handle_registration(email, password, user_name)
    elif type == "username":
        return username(email)
    elif type == "query":
        return handle_query(query_info)
    elif type == "subscribe":
        return handle_subscription(email, title, artist, year)
    elif type == 'get_subscribed_music':
        return get_subscribed_music(email)
    elif type == "remove_song": 
        return remove_song(email, title)
    else:
        return {
            'statusCode': 400,
            'body': '{"message": "Invalid request type"}'
        }

# This function is used to handle login functionalities. It checks the username and passsword matches with the login table.
def handle_login(email, password):
    try:
        # Getting the elements from login table by using the email
        response = table.get_item(Key={'email': email})
        
        if 'Item' in response:
            stored_password = response['Item']['password']
            # Checking the user entered password matches with the password stored in the table
            if password == stored_password:
                return {                                                
                    'statusCode': 200,
                    'body': f'{{"message": "Login successful", "email": "{email}", "password": "{password}"}}'
                }
            else:
                return {
                    'statusCode': 401,
                    'body': f'{{"message": "Incorrect password", "email": "{email}", "password": "{password}"}}'
                }
        else:
            return {
                'statusCode': 404,
                'body': f'{{"message": "Email not found", "email": "{email}", "password": "{password}"}}'
            }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }

# This function is used to handle registration. This helps new users to store the email, password and username in the login table.
def handle_registration(email, password, user_name):
    try:
        
        response = table.get_item(Key={'email': email})
        # Checking if the email is already present in the table.
        if 'Item' in response:
            return {
                'statusCode': 409,
                'body': '{"message": "The email already exists"}'
            }
        else:
            # Email does not exist, proceed with registration
            table.put_item(
                Item={
                    'email': email,
                    'user_name': user_name,
                    'password': password
                }
            )
            return {
                'statusCode': 200,
                'body': '{"message": "Registration successful"}'
            }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }


# This function is to handle the query. It takes input title, artist or year stored in query info, and scans the Music table with the filter conditions.

def handle_query(query_info):
    try:
        # Changing year into Integer format for querying
        if 'year' in query_info:
            query_info['year'] = int(query_info['year'])
        # Changing the table name to Music 
        table = dynamodb.Table('Music') 
        
        # calling the build_filter_expression function to build the query based on the input conditions.
        filter_expression, expression_attribute_names, expression_attribute_values = build_filter_expression(query_info)
        if not filter_expression:
            raise ValueError('FilterExpression is empty')
        
        # This is used to scan the table with generated filter 
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
        # Process the retrieved items and generate the response
        items = response['Items']
        
        
        music_info = []
        # Storing the required response in music_info and also adding the image of the artist in this
        for item in items:
            # Accessing the image of artist from s3 bucket. The image name is stored as {artistname without spaces}.jpg
            artist_name = item['artist'].replace(" ", "")
            
            # Generating pre-signed URL for the image for secured access
            image_url = generate_presigned_url('s3853674-music', f'images/{artist_name}.jpg')
            
            
            music_info.append({
                'title': item['title'],
                'artist': item['artist'],
                'year': str(item['year'] ),
                'image_url': image_url
               
            })
        
        return {
            'statusCode': 200,
            'music_info':music_info}
        
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': f'Error: {str(e)}'})
        }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': str(ve)})
        }


# This function is used to build the filter expression based on the user conditions.
def build_filter_expression(query_info):
    # Construct the FilterExpression based on the query information provided
    filter_expression = []
    expression_attribute_names = {}
    expression_attribute_values = {}
    
    # Checing each attribute is empty, if not, creating the filter.
    if 'title' in query_info:
        filter_expression.append('#title = :title_val')
        expression_attribute_names['#title'] = 'title'
        expression_attribute_values[':title_val'] = query_info['title']
    if 'year' in query_info:
        filter_expression.append('#year = :year_val')
        expression_attribute_names['#year'] = 'year'
        expression_attribute_values[':year_val'] = query_info['year']
    if 'artist' in query_info:
        filter_expression.append('#artist = :artist_val')
        expression_attribute_names['#artist'] = 'artist'
        expression_attribute_values[':artist_val'] = query_info['artist']
    
    # Joining the different filters with AND condition
    return ' AND '.join(filter_expression), expression_attribute_names, expression_attribute_values
    
    
# This function is used to fetch the username. This takes email as input and gets the relavant username
def username(email): 
    try:
        print("email",email)
        response = table.get_item(Key={'email': email})
        
        if 'Item' in response:
            
            user_name = response['Item']['user_name']
            return {
                'statusCode': 200,
                'username': user_name
            }
        else:
            return {
                'statusCode': 404,
                'body': '{"message": "Username not found"}'
            }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }


# This function is used to handle subscription. This function is triggered when someone clicks on subscribe button.
# this adds the newly requested music to Music Subscription table.
def handle_subscription( email, title, artist, year):
    try:
        # Changing the table to Music Subscription 
        table = dynamodb.Table('MusicSubscription')
        
        # Inserting the new items in the table
        table.put_item(
            Item={
                'email': email,
                'title': title,
                'artist': artist,
                'year': year
            }
        )
        return {
            'statusCode': 200,
            'body': '{"message": "Subscription successful"}'
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }

# This function is used to retrieve the subscribed music information for the required user.
def get_subscribed_music(email):
    try:
        table = dynamodb.Table('MusicSubscription')
        # Getting the response based on email as we only need to display that particular users music subscribed.
        response = table.scan(FilterExpression=Key('email').eq(email))
        items = response['Items']
        

        subscribed_music_info = []
        for item in items:
            artist_name = item['artist'].replace(" ", "")
            # Generating pre-signed URL for the image
            image_url = generate_presigned_url('s3853674-music', f'images/{artist_name}.jpg')
            subscribed_music_info.append({
                'title': item['title'],
                'artist': item['artist'],
                'year': item['year'],
                'image_url': image_url
            })

        return {
            'statusCode': 200,
            'subscribed_music_info': subscribed_music_info
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }


# This function is used to remove particular music from the users Music subscribed data.
def remove_song(email, title):
    try:
        table = dynamodb.Table('MusicSubscription')
        response = table.delete_item(
            Key={
                'email': email,
                'title': title
            }
        )
        return {
            'statusCode': 200,
            'body': '{"message": "Song removed successfully"}'
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': '{"message": "Internal Server Error"}'
        }
        
        
# This function is used to generate pre-signed URL.
# Code adapted from Amazon AWS docs
# https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html

def generate_presigned_url(bucket_name, object_key, expiration=3600):
    # Generating a pre-signed URL for the S3 object with a specified expiration time
    try:
        response = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key
            },
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating pre-signed URL: {str(e)}")
        return None