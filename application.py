from flask import Flask, jsonify
import boto3
from decouple import config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

AWS_ACCESS_KEY_ID     = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION           = config("AWS_REGION")
DYNAMODB_TABLE = 'Music'

# DynamoDB 클라이언트 생성
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/getData')
def get_dynamodb_data():
    try:
        # DynamoDB 테이블에서 데이터 가져오기
        response = dynamodb.scan(TableName=DYNAMODB_TABLE)
        items = response.get('Items', [])

        # 데이터를 JSON으로 변환하여 반환
        formatted_data = []
        for item in items:
            formatted_item = {
                "Artist": item["Artist"]["S"],
                "SongTitle": item["SongTitle"]["S"]
            }
            formatted_data.append(formatted_item)
    
        return jsonify(formatted_data)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)