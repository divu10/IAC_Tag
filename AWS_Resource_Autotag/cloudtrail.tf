#================ Cloudtrail ==================#
resource "aws_cloudtrail" "cloudtrail_autotag" {
  count                      = var.create_trail ? 1 : 0
  name                       = "${var.autotag_function_name}-trail"
  s3_bucket_name             = aws_s3_bucket.cloudtrail_bucket[count.index].id
  enable_log_file_validation = true
  cloud_watch_logs_role_arn  = aws_iam_role.lambda_exec_role.arn
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.lambda_log_grp.arn}:*"
  depends_on = [
    aws_s3_bucket.cloudtrail_bucket,
    aws_iam_role.lambda_exec_role,
    aws_cloudwatch_log_group.lambda_log_grp,
    aws_s3_bucket_policy.cloudtrail_bucket_policy
  ]
}

#============ Cloudtrail S3 Bucket ============#
resource "random_pet" "cloudtrail_bucket_name" {
  count  = var.create_trail ? 1 : 0
  prefix = "${var.autotag_function_name}-trail"
}

resource "aws_s3_bucket" "cloudtrail_bucket" {
  count         = var.create_trail ? 1 : 0
  bucket        = random_pet.cloudtrail_bucket_name[count.index].id
  force_destroy = true
}

resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  count  = var.create_trail ? 1 : 0
  bucket = aws_s3_bucket.cloudtrail_bucket[count.index].id
  policy = data.aws_iam_policy_document.cloudtrail_bucket_policy_doc[count.index].json
}

