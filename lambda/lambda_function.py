import json

def lambda_handler(event, context):
    if event['queryStringParameters'] is None:
        body=json.dumps(('this : '+'200'))
    else:
        body=json.dumps(('test : '+event['queryStringParameters']['var']))    
    return {
        'statusCode': 200,
        'body': body
    }