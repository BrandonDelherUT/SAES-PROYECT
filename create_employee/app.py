import json
import pymysql
import boto3
from botocore.exceptions import ClientError

def get_secret():
    secret_arn = 'arn:aws:secretsmanager:us-east-1:654654356618:secret:rds!db-0eb20036-5dec-4338-93c9-d1726c9f6919-v15ABH'
    region_name = 'us-east-1'

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_arn
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except ClientError as e:
        print(f"Error retrieving secret {secret_arn}: {str(e)}")
        raise Exception(f"Error retrieving secret {secret_arn}: {str(e)}")

def lambda_handler(event, context):
    secrets = get_secret()

    host = secrets['host']
    name = secrets['username']
    password = secrets['password']
    db_name = "SAES"

    connection = pymysql.connect(
        host=host,
        user=name,
        password=password,
        db=db_name,
        connect_timeout=5
    )

    try:
        with connection.cursor() as cursor:
            employee_data = json.loads(event['body'])
            insert_employee_sql = "INSERT INTO Employees (id_employee, name, role) VALUES (%s, %s, %s)"
            cursor.execute(insert_employee_sql, (employee_data['id_employee'], employee_data['name'], employee_data['role']))
            connection.commit()

        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "Employee created successfully"})
        }
    except pymysql.MySQLError as error:
        print(f"MySQL Error: {str(error)}")
        response = {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(error)})
        }
    except Exception as error:
        print(f"Error: {str(error)}")
        response = {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error", "error": str(error)})
        }
    finally:
        connection.close()
    return response
