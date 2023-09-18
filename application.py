from flask import Flask, jsonify
import boto3
from decouple import Config, RepositoryEnv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

config = Config(RepositoryEnv('./.env'))

AWS_ACCESS_KEY_ID     = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION           = config("AWS_REGION")
DYNAMODB_TABLE = 'Music'

S3_ACCESS_KEY_ID     = config("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = config("S3_SECRET_ACCESS_KEY")

# DynamoDB 클라이언트 생성
dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# S3 클라이언트 생성
s3 = boto3.client(
    's3',
    aws_access_key_id=S3_ACCESS_KEY_ID,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY,
    region_name=AWS_REGION)

# S3 버킷 목록 가져오기
response = s3.list_buckets()
for bucket in response['Buckets']:
    print('Bucket Name:', bucket['Name'])
    
# 특정 버킷의 객체 리스트 가져오기
bucket_name = 'blitz-data-ec2'  # 버킷 이름
prefix = 'S3-data'  # 가져올 객체들이 저장된 폴더 경로 또는 프리픽스

response = s3.list_objects(Bucket=bucket_name, Prefix=prefix)

# 객체 리스트 출력
for obj in response.get('Contents', []):
    print('Object Key:', obj['Key'])

# 라우팅
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
    app.run(host='0.0.0.0', debug=True)