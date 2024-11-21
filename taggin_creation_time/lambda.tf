#===================== Lambda Deployment Package=====================#
data "archive_file" "lambda_autotag" {
  type = "zip"

  source_dir  = "${path.module}/lambda-autotag/src"
  output_path = "${path.module}/lambda-autotag/lambda_package.zip"
}

#======================== Lambda Fucntion ========================#
resource "aws_lambda_function" "autotag" {
  function_name = var.autotag_function_name
  role          = aws_iam_role.lambda_exec_role.arn
  filename      = "${path.module}/lambda-autotag/lambda_package.zip"

  source_code_hash = data.archive_file.lambda_autotag.output_base64sha256

  runtime     = "python3.9"
  handler     = "lambda_function.lambda_handler"
  timeout     = 300
  memory_size = 128
}

#======================== Lambda Log Group ========================#
resource "aws_cloudwatch_log_group" "lambda_log_grp" {
  name              = "/aws/lambda/${var.autotag_function_name}"
  retention_in_days = 30
}
