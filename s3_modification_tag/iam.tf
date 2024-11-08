#======================== Lambda IAM Role and Policy ========================#
data "aws_iam_policy_document" "lambda_assume_role_policy" {
  statement {
    sid    = "LambdaAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    sid    = "CloudwatchAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudwatch.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    sid    = "CloudtrailAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    sid    = "EventsAssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }

  statement {
    sid    = "S3AssumeRole"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["s3.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "lambda_exec_role" {
  name               = "lambda-${var.autotag_function_name}"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json

  inline_policy {
    name   = "AutotagFunctionPermissions"
    policy = data.aws_iam_policy_document.lambda_inline_policy.json
  }
}

data "aws_iam_policy_document" "lambda_inline_policy" {
  # Policies for broader permissions related to resource creation events
  statement {
    sid    = "AllowTaggingOfResources"
    effect = "Allow"
    actions = [
      # DynamoDB
      "dynamodb:TagResource",
      "dynamodb:DescribeTable",

      # Lambdas
      "lambda:TagResource",
      "lambda:ListTags",

      # S3
      "s3:GetBucketTagging",
      "s3:PutBucketTagging",

      # EC2
      "ec2:CreateTags",
      "ec2:DescribeNatGateways",
      "ec2:DescribeInternetGateways",
      "ec2:DescribeVolumes",
      "ec2:DescribeVpcs",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeInstances",

      # RDS
      "rds:AddTagsToResource",
      "rds:DescribeDBInstances",

      # SNS
      "sns:TagResource",

      # SQS
      "sqs:ListQueueTags",
      "sqs:TagQueue",

      # OpenSearch
      "es:AddTags",

      # KMS
      "kms:ListResourceTags",
      "kms:TagResource",

      # EFS
      "elasticfilesystem:TagResource",
      "elasticfilesystem:CreateTags",
      "elasticfilesystem:DescribeTags",

      # ELB
      "elasticloadbalancing:AddTags",

      # CloudWatch
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",

      # Redshift
      "redshift:CreateTags",
      "redshift-serverless:TagResource",

      # Sagemaker
      "sagemaker:AddTags",

      # ECS
      "ecs:TagResource",

      # MSK
      "kafka:TagResource",

      # CloudWatch logs and alarms
      "logs:TagLogGroup",
      "cloudwatch:TagResource",

      # Amazon MQ
      "mq:CreateTags",

      # Resource Group Tag Editor
      "tag:getResources",
      "tag:getTagKeys",
      "tag:getTagValues",
      "tag:TagResources",
      "tag:UntagResources",
      "cloudformation:DescribeStacks",
      "cloudformation:ListStackResources",
      "resource-groups:*",
    ]
    resources = ["*"]
  }
}

#======================== Cloudtrail Bucket Policy ========================#
data "aws_iam_policy_document" "cloudtrail_bucket_policy_doc" {
  count = var.create_trail ? 1 : 0

  statement {
    sid    = "AllowCloudTrailCheckBucketAcl"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions   = ["s3:GetBucketAcl"]
    resources = [aws_s3_bucket.cloudtrail_bucket[count.index].arn]
  }

  statement {
    sid    = "AllowCloudTrailWriteLogs"
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.cloudtrail_bucket[count.index].arn}/AWSLogs/*"]
  }
}
