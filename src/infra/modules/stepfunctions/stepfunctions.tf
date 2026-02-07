variable "name_prefix" {
  type = string
}

variable "role_arn" {
  description = "IAM role ARN that the state machine will assume"
  type        = string
}

variable "state_machine_definition" {
  description = "ASL JSON definition for the state machine"
  type        = string
}

resource "aws_sfn_state_machine" "this" {
  name       = "${var.name_prefix}-step-functions-machine"
  role_arn   = var.role_arn
  definition = var.state_machine_definition
  type       = "STANDARD"
}

output "state_machine_name" {
  value = aws_sfn_state_machine.this.name
}

output "state_machine_arn" {
  value = aws_sfn_state_machine.this.arn
}
