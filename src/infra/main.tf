// Create IAM roles first
module "iam" {
  source = "./modules/iam"
  name_prefix = "${var.project}-${var.env}"
}

module "s3" {
  source = "./modules/s3"
  name_prefix = "${var.project}-${var.env}"
}

# Lambdas module (explicit simple variables)
module "lambdas" {
  source = "./modules/lambda"
  name_prefix = "${var.project}-${var.env}"
  ingestion_handler       = "main.handler"
  ingestion_runtime       = "python3.10"
  ingestion_role_arn      = module.iam.ingestion_role_arn
  ingestion_source_path   = var.ingestion_source_path

  compliance_handler       = "main.handler"
  compliance_runtime       = "python3.10"
  compliance_role_arn      = module.iam.compliance_role_arn
  compliance_source_path   = var.compliance_source_path
}


module "stepfunctions" {
  source = "./modules/stepfunctions"
  name_prefix = "${var.project}-${var.env}"
  role_arn = module.iam.sfn_role_arn
  state_machine_definition = templatefile("${path.module}/step-functions/definition.asl.json", {
    INGESTION_LAMBDA = module.lambdas.ingestion_lambda_arn
    COMPLIANCE_LAMBDA = module.lambdas.compliance_lambda_arn
  })
}

