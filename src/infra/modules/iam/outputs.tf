output "ingestion_role_arn" {
  value = aws_iam_role.ingestion.arn
}

output "compliance_role_arn" {
  value = aws_iam_role.compliance.arn
}

output "sfn_role_arn" {
  value = aws_iam_role.sfn.arn
}

output "ingestion_role_name" {
  value = aws_iam_role.ingestion.name
}

output "compliance_role_name" {
  value = aws_iam_role.compliance.name
}

output "sfn_role_name" {
  value = aws_iam_role.sfn.name
}
