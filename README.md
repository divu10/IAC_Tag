# AWS Resource Tagging Lambda Functions

This repository contains documentation and code for two Lambda functions designed to apply resource-level tags during the creation of AWS resources. These tags ensure resource governance, cost allocation, and traceability.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Lambda Functions](#lambda-functions)
  - [Creation-Time Tagging Lambda Function](#1-creation-time-tagging-lambda-function)
  - [Service-Specific Tagging Lambda Function](#2-service-specific-tagging-lambda-function)
- [Setup and Deployment](#setup-and-deployment)
- [Code Walkthrough](#code-walkthrough)
  - [General Code Features](#general-code-features)
  - [Service Handlers](#service-handlers)
- [Testing](#testing)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

These Lambda functions automate the tagging of AWS resources during their creation. The tags ensure compliance with organizational policies, improve resource traceability, and facilitate cost management.

---

## Features

- **Multi-Resource Support**: Handles EC2, DynamoDB, S3, EFS, and VPC Endpoints.
- **Mandatory Tagging Enforcement**: Applies tags such as `CreatedBy`, `CreatedOn`, `Division`, and `Studio`.
- **Dynamic Event Handling**: Listens to CloudTrail events and routes them to appropriate handlers.
- **Error Handling**: Logs issues and ensures smooth execution.

---

## Lambda Functions

### 1. Creation-Time Tagging Lambda Function

#### Purpose

This function automatically tags AWS resources at the time of their creation with organizationally defined tags:
- **CreatedBy**: Captures the creator of the resource.
- **CreatedOn**: Logs resource creation time (converted to IST).
- **Division** and **Studio**: Defined through environment variables.

#### Key Features

1. **Event Handling**:
   - Listens to CloudTrail events.
   - Routes events to specific service handlers.
2. **Dynamic Tagging Logic**:
   - Constructs ARNs dynamically.
   - Calls `tag_resources` API for tagging.
3. **Helper Functions**:
   - Extracts identity and converts timestamps to IST.
   - Handles missing or malformed data gracefully.

#### Supported Services

- EC2
- S3
- DynamoDB
- Elastic File System (EFS)

---

### 2. Service-Specific Tagging Lambda Function

#### Purpose

Provides detailed tagging logic for specific AWS services, focusing on dynamic ARN construction and robust error handling.

#### Key Features

1. **Service-Specific Handlers**:
   - **S3**: Tags buckets on creation by constructing ARNs using bucket names.
   - **Elastic File System (EFS)**: Tags file systems by identifying `CreateMountTarget` events.
   - **DynamoDB**: Waits for table creation to complete before applying tags.
   - **VPC Endpoint**: Tags VPC endpoints dynamically during creation.

2. **Dynamic ARN Construction**:
   - Uses templates and event details to generate ARNs for newly created resources.

3. **Error Handling**:
   - Captures and logs errors to facilitate debugging.

---

## Setup and Deployment

### Prerequisites

- AWS Lambda function with the necessary IAM permissions to tag resources.
- CloudTrail enabled to capture resource creation events.

### Deployment

1. **Upload the Code**:
   - Add the Python script to an AWS Lambda function.
2. **Assign IAM Role**:
   - Ensure the execution role includes permissions for:
     - `resourcegroupstaggingapi:TagResources`
     - `ec2:CreateTags`
     - `dynamodb:TagResource`
     - `s3:PutBucketTagging`
     - `efs:TagResource`
3. **Configure EventBridge**:
   - Set up EventBridge rules to trigger the Lambda function on resource creation events.

---

## Code Walkthrough

### General Code Features

1. **Imports and Logging**:
   - Imports required AWS SDKs (`boto3`) and configures logging.
2. **Event Routing**:
   - Routes resource creation events to the appropriate service handler.

3. **Mandatory Tags**:
   - Tags are defined dynamically through environment variables (`DIVISION`, `STUDIO`).

### Service Handlers

#### EC2 Handler

- Identifies VPC Endpoint creation events.
- Constructs ARNs dynamically and applies mandatory tags.

#### DynamoDB Handler

- Waits for the table creation process to complete.
- Uses `DescribeTable` API to retrieve ARNs.

#### S3 Handler

- Tags buckets on creation by generating ARNs using bucket names.

#### EFS Handler

- Applies tags for Elastic File Systems by identifying `CreateMountTarget` events.

---

## Testing

### Test Scenarios

1. **Successful Tagging**:
   - Verified for S3, DynamoDB, EFS, and VPC Endpoints.
2. **Error Handling**:
   - Simulated missing tags or malformed events to ensure graceful failure.
3. **Performance**:
   - Tested function execution across multiple resource creations.

---

## Best Practices

1. **Error Resilience**:
   - Logs and recovers from failures during tagging.
2. **Dynamic Tagging**:
   - Uses event details to construct ARNs dynamically.
3. **Environment Variables**:
   - Avoids hardcoding tags by using environment variables.

---

## Future Enhancements

1. **Support Additional Services**:
   - Extend handlers to support services like RDS, Lambda, and more.
2. **Advanced Tag Policies**:
   - Incorporate conditional tagging based on resource metadata.
3. **Monitoring and Metrics**:
   - Use CloudWatch metrics to monitor tagging success rates.

---

## License

This project is licensed under the [MIT License](LICENSE).

---
