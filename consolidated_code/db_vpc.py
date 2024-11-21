import boto3

# Lambda function for handling EC2 tags
def handle_ec2_tags(event):
    ec2_client = boto3.client('ec2')
    print(f"Received event for EC2: {event}")

    try:
        if 'detail' not in event:
            print("Missing 'detail' in event")
            return {"statusCode": 400, "body": "Missing 'detail' in event"}

        event_name = event['detail'].get('eventName')
        print(f"Event name: {event_name}")

        user_identity = event['detail'].get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', ''):
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        if event_name not in ['CreateTags', 'DeleteTags']:
            print(f"Unsupported event: {event_name}")
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

        resource_items = event["detail"]["requestParameters"]["resourcesSet"]["items"]
        if not resource_items or "resourceId" not in resource_items[0]:
            print("Resource ID not found in the event")
            return {"statusCode": 400, "body": "Resource ID not found in the event"}

        resource_id = resource_items[0]["resourceId"]
        print(f"Resource ID: {resource_id}")

        current_tags_response = ec2_client.describe_tags(
            Filters=[{'Name': 'resource-id', 'Values': [resource_id]}]
        )
        current_tags = current_tags_response.get('Tags', [])
        current_tags_dict = {tag['Key']: tag['Value'] for tag in current_tags}

        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]

        if event_name == 'DeleteTags':
            print(f"Handling DeleteTags for {resource_id}")
            ec2_client.create_tags(
                Resources=[resource_id],
                Tags=[tag for tag in mandatory_tags if tag['Key'] not in current_tags_dict]
            )
            print(f"Re-applied mandatory tags for {resource_id}")
            return {"statusCode": 200, "body": f"Re-applied mandatory tags for {resource_id}"}

        elif event_name == 'CreateTags':
            print(f"Handling CreateTags for {resource_id}")
            tags_to_apply = []
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_dict:
                    tags_to_apply.append(mandatory_tag)

            if tags_to_apply:
                ec2_client.create_tags(
                    Resources=[resource_id],
                    Tags=tags_to_apply
                )
                print(f"Added missing mandatory tags: {tags_to_apply}")
            else:
                print("All mandatory tags are already present.")
            return {"statusCode": 200, "body": f"Tags validated for {resource_id}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}

# Lambda function for handling DynamoDB tags
def handle_dynamodb_tags(event):
    dynamodb_client = boto3.client('dynamodb')
    print(f"Received event for DynamoDB: {event}")

    try:
        event_detail = event.get('detail', event)
        event_name = event_detail.get('eventName')
        if not event_name:
            print("Event name not found in event")
            return {"statusCode": 400, "body": "Event name not found"}

        print(f"Event name: {event_name}")

        user_identity = event_detail.get('userIdentity', {})
        if user_identity.get('type') == "AssumedRole" and "autotag" in user_identity.get('arn', '') and event_name == "TagResource":
            print("Event triggered by Lambda itself; skipping to avoid loop.")
            return {"statusCode": 200, "body": "Ignored event to prevent infinite loop"}

        if event_name not in ['TagResource', 'UntagResource']:
            print(f"Unsupported event: {event_name}")
            return {"statusCode": 400, "body": f"Unsupported event: {event_name}"}

        resource_arn = event_detail.get("requestParameters", {}).get("resourceArn")
        if not resource_arn:
            print("ResourceArn not found in the event")
            return {"statusCode": 400, "body": "ResourceArn not found in the event"}

        print(f"ResourceArn: {resource_arn}")

        try:
            current_tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=resource_arn)
            current_tags = current_tags_response.get('Tags', [])
        except dynamodb_client.exceptions.ClientError as e:
            print(f"Error fetching current tags: {e}")
            return {"statusCode": 500, "body": f"Error fetching tags: {str(e)}"}

        mandatory_tags = [
            {'Key': 'Division', 'Value': 'CD'},
            {'Key': 'Studio', 'Value': 'Ajax'}
        ]
        current_tags_dict = {tag['Key']: tag['Value'] for tag in current_tags}

        if event_name == 'UntagResource':
            print(f"Handling UntagResource for {resource_arn}")
            dynamodb_client.tag_resource(
                ResourceArn=resource_arn,
                Tags=mandatory_tags
            )
            print(f"Re-applied tags for {resource_arn}")
            return {"statusCode": 200, "body": f"Tags re-applied for {resource_arn}"}

        elif event_name == 'TagResource':
            print(f"Handling TagResource for {resource_arn}")
            tags_to_apply = current_tags.copy()
            for mandatory_tag in mandatory_tags:
                if mandatory_tag['Key'] not in current_tags_dict:
                    print(f"Adding missing mandatory tag: {mandatory_tag}")
                    tags_to_apply.append(mandatory_tag)

            dynamodb_client.tag_resource(
                ResourceArn=resource_arn,
                Tags=tags_to_apply
            )
            print(f"Tags applied for {resource_arn}: {tags_to_apply}")
            return {"statusCode": 200, "body": f"Tags handled for {resource_arn}"}

    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}

# Combined handler
def lambda_handler(event, context):
    # Determine service based on event details
    if 'ec2' in str(event).lower():
        return handle_ec2_tags(event)
    elif 'dynamodb' in str(event).lower():
        return handle_dynamodb_tags(event)
    else:
        return {"statusCode": 400, "body": "Unsupported service in event"}
