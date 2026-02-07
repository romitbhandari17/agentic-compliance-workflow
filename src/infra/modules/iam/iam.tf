variable "name_prefix" {
  type = string
}

# Ingestion Lambda execution role
resource "aws_iam_role" "ingestion" {
  name = "${var.name_prefix}-ingestion-lambda-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

data "aws_iam_policy_document" "ingestion_policy_doc" {
  statement {
    sid = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }

  statement {
    sid = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponse"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ingestion_policy" {
  name = "ingestion-inline-policy"
  role = aws_iam_role.ingestion.id
  policy = data.aws_iam_policy_document.ingestion_policy_doc.json
}

# Compliance Lambda execution role
resource "aws_iam_role" "compliance" {
  name = "${var.name_prefix}-compliance-lambda-exec-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "lambda.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

data "aws_iam_policy_document" "compliance_policy_doc" {
  statement {
    sid = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }

  statement {
    sid = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponse"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "Textract"
    effect = "Allow"
    actions = [
      "textract:DetectDocumentText",
      "textract:AnalyzeDocument",
      "textract:StartDocumentTextDetection",
      "textract:GetDocumentTextDetection",
      "textract:StartDocumentAnalysis",
      "textract:GetDocumentAnalysis"
    ]
    resources = ["*"]
  }

  statement {
    sid    = "S3ReadForTextract"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListBucket"
    ]
    resources = ["*"]
  }

}

resource "aws_iam_role_policy" "compliance_policy" {
  name = "compliance-inline-policy"
  role = aws_iam_role.compliance.id
  policy = data.aws_iam_policy_document.compliance_policy_doc.json
}

# Step Functions execution role (able to invoke Lambdas only)
resource "aws_iam_role" "sfn" {
  name = "${var.name_prefix}-sfn-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = { Service = "states.amazonaws.com" },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

data "aws_iam_policy_document" "sfn_invoke_policy_doc" {
  statement {
    sid = "InvokeLambdas"
    effect = "Allow"
    actions = ["lambda:InvokeFunction"]
    resources = ["*"]
  }

  statement {
    sid = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "sfn_invoke_policy" {
  name = "sfn-invoke-lambda-policy"
  role = aws_iam_role.sfn.id
  policy = data.aws_iam_policy_document.sfn_invoke_policy_doc.json
}
