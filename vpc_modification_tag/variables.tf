#============ Input variable definitions ============#
variable "aws_region" {
  description = "AWS region for all resources."
  type        = string
  default     = "us-east-1"
}

variable "create_trail" {
  description = "Check if a Cloudtrail trail for management events exists. Set to false if it exists"
  type        = bool
  default     = true
}

variable "autotag_function_name" {
  description = "Name of lambda function"
  type        = string
  default     = "autotag"
}
