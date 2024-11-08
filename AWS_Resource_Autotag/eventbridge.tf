#============ Eventbridge Rules ============#
resource "aws_cloudwatch_event_rule" "resource_creation_rule" {
  name          = "${var.autotag_function_name}-event-rule"
  description   = "Triggers Lambda when resources are created"
  event_pattern = <<EOF
{
  "source": [
    "aws.ec2",
    "aws.elasticloadbalancing", 
    "aws.rds", 
    "aws.lambda", 
    "aws.s3", 
    "aws.dynamodb", 
    "aws.elasticfilesystem", 
    "aws.es", 
    "aws.sqs", 
    "aws.sns", 
    "aws.kms", 
    "aws.ecs", 
    "aws.redshift", 
    "aws.redshift-serverless", 
    "aws.sagemaker", 
    "aws.monitoring", 
    "aws.logs", 
    "aws.kafka", 
    "aws.amazonmq"
  ],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": [
      "ec2.amazonaws.com",
      "elasticloadbalancing.amazonaws.com",
      "s3.amazonaws.com",
      "rds.amazonaws.com",
      "lambda.amazonaws.com",
      "dynamodb.amazonaws.com",
      "elasticfilesystem.amazonaws.com",
      "es.amazonaws.com",
      "sqs.amazonaws.com",
      "sns.amazonaws.com",
      "kms.amazonaws.com",
      "redshift.amazonaws.com",
      "redshift-serverless.amazonaws.com",
      "sagemaker.amazonaws.com",
      "ecs.amazonaws.com",
      "monitoring.amazonaws.com",
      "logs.amazonaws.com",
      "kafka.amazonaws.com",
      "amazonmq.amazonaws.com"
    ],
    "eventName": [
      "RunInstances",
      "CreateVpc",
      "CreateSecurityGroup",
      "CreateSubnet",
      "CreateFunction20150331",
      "CreateBucket",
      "CreateDBInstance",
      "CreateTable",
      "CreateVolume",
      "CreateLoadBalancer",
      "CreateInternetGateway",
      "CreateNatGateway",
      "AllocateAddress",
      "CreateVpcEndpoint",
      "CreateTransitGateway",
      "CreateMountTarget",
      "CreateDomain",
      "CreateQueue",
      "CreateTopic",
      "CreateKey",
      "CreateCluster",
      "CreateClusterV2",
      "CreateNotebookInstance",
      "PutMetricAlarm",
      "CreateLogGroup",
      "CreateBroker",
      "CreateNamespace",
      "CreateWorkgroup",
      "CreateProcessingJob",
      "CreateEndpoint",
      "CreateModel",
      "CreateLabelingJob",
      "CreateTrainingJob",
      "CreateTransformJob",
      "CreateUserProfile",
      "CreateWorkteam"
    ]
  }
}
EOF
}

#============ Eventbridge Targets ============
resource "aws_cloudwatch_event_target" "lambda" {
  rule       = aws_cloudwatch_event_rule.resource_creation_rule.id
  target_id  = "SendToLambda"
  arn        = aws_lambda_function.autotag.arn
  depends_on = [aws_lambda_function.autotag]
}

resource "aws_lambda_permission" "event_bridge_rule" {
  statement_id  = "AllowExecutionFromEventBridgeRule"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.autotag.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.resource_creation_rule.arn
  depends_on = [
    aws_lambda_function.autotag,
    aws_cloudwatch_event_rule.resource_creation_rule
  ]
}
