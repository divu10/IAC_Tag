import boto3

def lambda_handler(event, context):
    # Initialize the S3 client inside the handler function
    s3_client = boto3.client('s3')
    
    # Log the entire incoming event
    print(f"Received event: {event}")  

    try:
        # Check if 'detail' is in the event
        if 'detail' not in event:
            print("Missing 'detail' in event")  # Log missing detail
            return {"statusCode": 400, "body": "Missing 'detail' in event"}

        # Capture event name from the nested 'detail' key
        event_name = event['detail'].get('eventName')
        print(f"Event name: {event_name}")  # Log the event name
        
        if 'userIdentity' in event['detail']:
            user_identity = event['detail']['userIdentity']['type']
            role_arn = event['detail']['userIdentity']['arn']
            if user_identity == "AssumedRole" and "autotag" in role_arn and event_name == "PutBucketTagging":
                print("Event triggered by Lambda itself; skipping to avoid loop.")
                return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        # Handle only specific events
        if event_name not in ['PutBucketTagging', 'DeleteBucketTagging']:
            print(f"Unsupported event: {event_name}")  # Log unsupported event
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

        # Extract bucket name from the 'requestParameters' key within 'detail'
        bucket_name = event["detail"]["requestParameters"].get("bucketName")
        print(f"Bucket name: {bucket_name}")  # Log the bucket name

        # Check if bucket_name was extracted correctly
        if not bucket_name:
            print("Bucket name not found in the event")  # Log missing bucket name
            return {"statusCode": 400, "body": "Bucket name not found in the event"}

        # Retrieve current tags to check if the Lambda has already processed this bucket
        try:
            current_tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
            current_tags = current_tags_response['TagSet']
        except s3_client.exceptions.ClientError as e:
            # Handle the case where the bucket has no tags set yet
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                current_tags = []
            else:
                print(f"Error fetching current tags: {e}")
                return {"statusCode": 500, "body": str(e)}

        # Check if Lambda has already processed this bucket by looking for 'LambdaProcessed' tag
        current_tags_set = {tag['Key']: tag['Value'] for tag in current_tags}
        if current_tags_set.get("LambdaProcessed") == "True":
            print("Bucket already processed by Lambda, skipping...")
            return {"statusCode": 200, "body": "Bucket already processed by Lambda"}

        # Define mandatory tags to be applied
        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}  
        ]

        # Handle DeleteBucketTagging by re-applying the mandatory tags
        if event_name == 'DeleteBucketTagging':
            response = s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={'TagSet': mandatory_tags}
            )
            print(f"Re-applied tags for {bucket_name}")  # Log the re-application action
            print(f"Response from put_bucket_tagging: {response}")  # Log the response

        # Handle PutBucketTagging
        elif event_name == 'PutBucketTagging':
            # Check for mandatory tags and ensure they are present
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_set:
                    print(f"Mandatory tag {mandatory_tag['Key']} not found, adding...")  # Log missing tag
                    current_tags.append(mandatory_tag)  # Add mandatory tag if missing
                else:
                    print(f"Mandatory tag {mandatory_tag['Key']} already present.")

            # Re-apply the tags including mandatory ones
            response = s3_client.put_bucket_tagging(
                Bucket=bucket_name,
                Tagging={'TagSet': current_tags}
            )
            print(f"Tags applied for {bucket_name}: {current_tags}")  # Log the applied tags
            print(f"Response from put_bucket_tagging: {response}")  # Log the response

        return {"statusCode": 200, "body": f"Tags handled for {bucket_name}"}
    
    except Exception as e:
        print(f"Error: {e}")  # Log any error encountered
        return {"statusCode": 500, "body": str(e)}
