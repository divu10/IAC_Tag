# ============ EventBridge Rules ============
resource "aws_cloudwatch_event_rule" "resource_creation_rule" {
  name          = "${var.autotag_function_name}-event-rule"
  description   = "Triggers Lambda when resources are tagged"
  event_pattern = <<EOF
{
  "source": [
    "aws.s3", 
    "aws.dynamodb", 
    "aws.elasticfilesystem",
    "aws.ec2"
  ],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": [
      "s3.amazonaws.com",
      "rds.amazonaws.com",
      "dynamodb.amazonaws.com",
      "elasticfilesystem.amazonaws.com",
      "es.amazonaws.com",
      "ec2.amazonaws.com"
    ],
    "eventName": [
      "PutBucketTagging",
      "DeleteBucketTagging",
      "TagResource",
      "UntagResource",
      "CreateTags",
      "DeleteTags"
    ]
  }
}
EOF
}

# ============ EventBridge Targets ============
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
