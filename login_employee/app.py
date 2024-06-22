import json
import boto3
import bcrypt

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'Employees'

def lambda_handler(event, context):
    username = event['username']
    password = event['password']

    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={'username': username})

    if 'Item' not in response:
        return {
            'statusCode': 401,
            'body': json.dumps('Invalid credentials')
        }

    stored_password = response['Item']['password']
    if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
        return {
            'statusCode': 200,
            'body': json.dumps('Login successful')
        }
    else:
        return {
            'statusCode': 401,
            'body': json.dumps('Invalid credentials')
        }
