def handle_ec2_event(event_detail, ec2_client, mandatory_tags):
    # Extract the resource ID from the event
    resource_items = event_detail.get("requestParameters", {}).get("resourcesSet", {}).get("items", [])
    if not resource_items or "resourceId" not in resource_items[0]:
        print("Resource ID not found in the event")
        return {"statusCode": 400, "body": "Resource ID not found in the event"}

    resource_id = resource_items[0]["resourceId"]
    print(f"Resource ID: {resource_id}")

    try:
        # Apply the mandatory tags to the EC2 instance
        ec2_client.create_tags(
            Resources=[resource_id],
            Tags=[{"Key": tag['Key'], "Value": tag['Value']} for tag in mandatory_tags]
        )
        print(f"Tags applied to EC2 instance {resource_id}: {mandatory_tags}")
        return {"statusCode": 200, "body": f"Tags handled for EC2 instance {resource_id}"}
    except Exception as e:
        print(f"Error applying tags to EC2 instance: {e}")
        return {"statusCode": 500, "body": str(e)}
