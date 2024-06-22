import json
import pymysql
import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, __):
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
            select_employee_sql = "SELECT * FROM Employees WHERE id_employee = %s"
            cursor.execute(select_employee_sql, (id_employee,))
            employee = cursor.fetchone()

        response = {
            "statusCode": 200,
            "body": json.dumps({"employee": employee})
        }
    except pymysql.MySQLError as error:
        response = {
            "statusCode": 500,
            "body": str(error)
        }
    finally:
        connection.close()
    return response


def get_secret():
    secret_name = "dev/Saes/Mysql"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )

    except ClientError as e:
        print(e.response['Error']['Code'])
        raise e

    return get_secret_value_response['SecretString']

    # Your code goes here.
