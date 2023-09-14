from flask import Flask, jsonify
import boto3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# AWS 계정 및 리전 설정
aws_access_key_id = '' # 발급 권한 없음
aws_secret_access_key = '' # 발급 권한 없음
aws_region = 'ap-northeast-2'
dynamodb_table_name = 'Music'

# DynamoDB 클라이언트 생성
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

@app.route('/api/getData')
def get_dynamodb_data():
    try:
        # DynamoDB 테이블에서 데이터 가져오기
        response = dynamodb.scan(TableName=dynamodb_table_name)
        items = response.get('Items', [])

        # 데이터를 JSON으로 변환하여 반환
        data = [{'id': item['id']['S'], 'name': item['name']['S']} for item in items]
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)