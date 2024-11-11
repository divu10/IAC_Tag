import json

# Assuming the JSON event is stored in a variable called event_json
event_json = '''{
  "eventVersion": "1.10",
  "userIdentity": {
    "type": "Root",
    "principalId": "361769560345",
    "arn": "arn:aws:iam::361769560345:root",
    "accountId": "361769560345",
    "accessKeyId": "ASIAVIOZFNEM2SGMYU4K",
    "sessionContext": {
      "attributes": {
        "creationDate": "2024-10-24T08:59:04Z",
        "mfaAuthenticated": "false"
      }
    }
  },
  "eventTime": "2024-10-24T09:20:40Z",
  "eventSource": "s3.amazonaws.com",
  "eventName": "DeleteBucketTagging",
  "awsRegion": "us-east-1",
  "sourceIPAddress": "103.62.237.178",
  "userAgent": "[Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36]",
  "requestParameters": {
    "tagging": "",
    "bucketName": "alphalion",
    "Host": "s3.amazonaws.com"
  },
  "responseElements": null,
  "additionalEventData": {
    "SignatureVersion": "SigV4",
    "CipherSuite": "TLS_AES_128_GCM_SHA256",
    "bytesTransferredIn": 0,
    "AuthenticationMethod": "AuthHeader",
    "x-amz-id-2": "J+W58j+AI4iw8huws39ohROm1lmdB2RySnOQ5A9UqWTx5HU6rdD0FdA7617MEjNDM8wUzRw6rvM=",
    "bytesTransferredOut": 0
  },
  "requestID": "1Y0GHA0RM375JRBS",
  "eventID": "83904920-0c2f-4d64-8334-3b6cd22f7128",
  "readOnly": false,
  "resources": [
    {
      "accountId": "361769560345",
      "type": "AWS::S3::Bucket",
      "ARN": "arn:aws:s3:::alphalion"
    }
  ],
  "eventType": "AwsApiCall",
  "managementEvent": true,
  "recipientAccountId": "361769560345",
  "eventCategory": "Management",
  "tlsDetails": {
    "tlsVersion": "TLSv1.3",
    "cipherSuite": "TLS_AES_128_GCM_SHA256",
    "clientProvidedHostHeader": "s3.amazonaws.com"
  }
}'''

# Parse the JSON data
event_data = json.loads(event_json)

# Extract the bucket name
bucket_name = event_data['requestParameters']['bucketName']

print("Bucket Name:", bucket_name)
