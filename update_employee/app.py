import json
import pymysql
import boto3
from botocore.exceptions import ClientError

def get_secret():
    secret_name = 'rds!db-0eb20036-5dec-4338-93c9-d1726c9f6919'
    region_name = 'us-east-1'

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)
    except ClientError as e:
        raise Exception(f"Error retrieving secret {secret_name}: {str(e)}")

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
            update_employee_sql = "UPDATE Employees SET name = %s, role = %s WHERE id_employee = %s"
            cursor.execute(update_employee_sql, (employee_data['name'], employee_data['role'], employee_data['id_employee']))
            connection.commit()

        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "Employee updated successfully"})
        }
    except pymysql.MySQLError as error:
        response = {
            "statusCode": 500,
            "body": str(error)
        }
    finally:
        connection.close()
    return response
