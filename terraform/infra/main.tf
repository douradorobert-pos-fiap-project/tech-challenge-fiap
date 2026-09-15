data "terraform_remote_state" "shared" {
  backend = "s3"

  config = {
    bucket = "terraform-state-264040538379-us-east-1"
    key    = "sandbox/terraform.tfstate"
    region = "us-east-1"
  }
}

data "terraform_remote_state" "database" {
  backend = "s3"

  config = {
    bucket = "terraform-state-264040538379-us-east-1"
    key    = "database/terraform.tfstate"
    region = "us-east-1"
  }
}

data "aws_secretsmanager_secret_version" "jwt" {
  secret_id = data.terraform_remote_state.shared.outputs.jwt_secret_arn
}
