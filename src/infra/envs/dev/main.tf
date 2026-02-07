# This file calls the root infra module and passes environment-specific variables.
module "infra" {
  source = "../.."

  env = var.env
  project = var.project
  region = var.region

  ingestion_source_path   = var.ingestion_source_path

  compliance_source_path   = var.compliance_source_path
}
