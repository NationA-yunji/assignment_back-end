from flask import Flask, jsonify
import boto3
from botocore.exceptions import NoCredentialsError
from decouple import Config, RepositoryEnv
from flask_cors import CORS
import logging

logger = logging.getLogger(__name__)

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
    
# 미리 서명된 URL 생성 함수
def generate_signed_url(s3_client, client_method, method_parameters, expiration_time):
    try:
        # 서명된 URL 생성
        signed_url = s3_client.generate_presigned_url(
            ClientMethod = client_method, # 클라이언트 메서드
            Params=method_parameters, # 클라이언트 메서드 파라미터
            ExpiresIn=expiration_time # signed URL 유효기간
        )
        logger.info("Got presigned URL: %s", signed_url)
        return signed_url
    except NoCredentialsError as e:
        error_message = "AWS credentials not found. Please check your configuration."
        logger.error(error_message)
        return {'error': error_message}, 500 

# 라우팅
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/api/get-data')
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

@app.route('/api/get-signed-url')
def get_signed_url():
    # 서명된 URL 생성
    # Bucket = 버킷명 / Key = 버킷 내의 객체 경로 또는 키
    signed_url = generate_signed_url(s3, 'get_object', {'Bucket': bucket_name, 'Key': 'S3-data/profile_bl.png'}, 3600)
    return jsonify(signed_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)