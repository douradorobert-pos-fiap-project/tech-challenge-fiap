output "rds_endpoint" {
  value = data.terraform_remote_state.database.outputs.rds_endpoint
}

output "rds_port" {
  value = tostring(data.terraform_remote_state.database.outputs.rds_port)
}

output "database_name" {
  value = data.terraform_remote_state.database.outputs.database_name
}

output "database_username" {
  value = data.terraform_remote_state.database.outputs.database_username
}

output "eks_cluster_name" {
  value = data.terraform_remote_state.shared.outputs.eks_cluster_name
}

output "ecr_repository_url" {
  value = data.terraform_remote_state.shared.outputs.ecr_application_repository_url
}

output "lambda_arn" {
  value = data.terraform_remote_state.shared.outputs.lambda_arn
}

output "eks_node_role_arn" {
  value = data.terraform_remote_state.shared.outputs.eks_node_role_arn
}

output "jwt_secret" {
  sensitive = true
  value     = jsondecode(data.aws_secretsmanager_secret_version.jwt.secret_string)["secret"]
}
