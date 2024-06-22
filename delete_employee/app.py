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
            id_employee = event['queryStringParameters']['id_employee']

            update_users_sql = "UPDATE Users SET fk_id_employee = NULL WHERE fk_id_employee = %s"
            cursor.execute(update_users_sql, (id_employee,))
            connection.commit()

            delete_employee_sql = "DELETE FROM Employees WHERE id_employee = %s"
            cursor.execute(delete_employee_sql, (id_employee,))
            connection.commit()

        response = {
            "statusCode": 200,
            "body": json.dumps({"message": "Employee deleted successfully"})
        }
    except pymysql.MySQLError as error:
        response = {
            "statusCode": 500,
            "body": str(error)
        }
    finally:
        connection.close()
    return response
