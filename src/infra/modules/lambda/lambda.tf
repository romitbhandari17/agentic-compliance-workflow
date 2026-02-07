variable "name_prefix" {
  type = string
}

variable "ingestion_handler" {
  type    = string
  default = "main.handler"
}

variable "ingestion_runtime" {
  type    = string
  default = "python3.10"
}

variable "ingestion_role_arn" {
  type = string
}

variable "ingestion_source_path" {
  type = string
}

variable "ingestion_memory_size" {
  type    = number
  default = 512
}

# Compliance variables
variable "compliance_handler" {
  type    = string
  default = "main.handler"
}

variable "compliance_runtime" {
  type    = string
  default = "python3.10"
}

variable "compliance_role_arn" {
  type = string
}

variable "compliance_source_path" {
  type = string
}

variable "compliance_memory_size" {
  type    = number
  default = 512
}

# Ingestion Lambda (explicit resource)
resource "aws_lambda_function" "ingestion" {
  function_name = "${var.name_prefix}-ingestion"
  handler       = var.ingestion_handler
  runtime       = var.ingestion_runtime
  role          = var.ingestion_role_arn

  filename         = var.ingestion_source_path
  source_code_hash = filebase64sha256(var.ingestion_source_path)

  memory_size = var.ingestion_memory_size
  timeout = 300
}

# Compliance Lambda (explicit resource)
resource "aws_lambda_function" "compliance" {
  function_name = "${var.name_prefix}-compliance"
  handler       = var.compliance_handler
  runtime       = var.compliance_runtime
  role          = var.compliance_role_arn

  filename         = var.compliance_source_path
  source_code_hash = filebase64sha256(var.compliance_source_path)

  memory_size = var.compliance_memory_size
  timeout = 300
}
