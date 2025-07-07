import json
import boto3
import random
import string
from urllib.parse import urlparse

s3 = boto3.client('s3')
BUCKET_NAME = "serverless-url-shortner-1"
MAPPING_FILE = "urls.json"

def lambda_handler(event, context):
    print("===== Received event =====")
    print(json.dumps(event, indent=2))

    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters', {})

        # POST /shorten
        if http_method == 'POST' and path.endswith('/shorten'):
            try:
                body = json.loads(event.get('body', '{}'))
                long_url = body.get('longUrl', '').strip()

                if not long_url:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Missing longUrl'})
                    }

                if not urlparse(long_url).scheme:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Invalid URL'})
                    }

                try:
                    obj = s3.get_object(Bucket=BUCKET_NAME, Key=MAPPING_FILE)
                    url_mappings = json.loads(obj['Body'].read().decode('utf-8'))
                except s3.exceptions.NoSuchKey:
                    url_mappings = {}

                short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                while short_code in url_mappings:
                    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

                url_mappings[short_code] = long_url
                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=MAPPING_FILE,
                    Body=json.dumps(url_mappings),
                    ContentType='application/json'
                )

                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'shortUrl': short_code})
                }

            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON'})
                }

        # GET /shortCode/{shortCode}
        elif http_method == 'GET' and 'shortCode' in path:
            short_code = path_parameters.get('shortCode', '') or path.split('/')[-1]

            if not short_code:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Missing shortCode'})
                }

            try:
                obj = s3.get_object(Bucket=BUCKET_NAME, Key=MAPPING_FILE)
                url_mappings = json.loads(obj['Body'].read().decode('utf-8'))

                if short_code in url_mappings:
                    return {
                        'statusCode': 200,
                        'headers': {'Content-Type': 'application/json'},
                        'body': json.dumps({'location': url_mappings[short_code]})
                    }
                else:
                    return {
                        'statusCode': 404,
                        'body': json.dumps({'error': 'Short URL not found'})
                    }

            except s3.exceptions.NoSuchKey:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'error': 'Mapping file not found'})
                }

        # Fallback for anything else
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Invalid endpoint'})
        }

    except Exception as e:
        print("Unhandled error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
