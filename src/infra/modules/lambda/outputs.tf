output "ingestion_lambda_arn" {
  value = aws_lambda_function.ingestion.arn
}

output "compliance_lambda_arn" {
  value = aws_lambda_function.compliance.arn
}