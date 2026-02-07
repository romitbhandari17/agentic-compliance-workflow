variable "name_prefix" {
  type = string
}

resource "aws_s3_bucket" "this" {
  bucket = "${var.name_prefix}-s3-artifacts"
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.bucket

  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_id" {
  value = aws_s3_bucket.this.id
}

output "bucket_arn" {
  value = aws_s3_bucket.this.arn
}
