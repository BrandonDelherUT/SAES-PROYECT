from read_employee import app
import unittest

mock_data = {
    "queryStringParameters": {
        "id_employee": "1"
    }
}


class TestApp(unittest.TestCase):
    def test_lambda_handler(self):
        app.lambda_handler(mock_data, None)

