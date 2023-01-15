import json

def lambda_handler(event, context):
    if event['queryStringParameters'] is None:
        body=json.dumps(('Default : '+'200'))
    else:
        body=json.dumps(('Input : '+event['queryStringParameters']['var']))    
    return {
        'statusCode': 200,
        'body': body
    }