output "cluster_name" {
  description = "Nome do cluster Kind criado"
  value       = kind_cluster.oficina.name
}

output "cluster_endpoint" {
  description = "Endpoint do cluster Kubernetes"
  value       = kind_cluster.oficina.endpoint
}

output "api_url" {
  description = "URL de acesso a API (NodePort via port-forward)"
  value       = "http://localhost:8080"
}

output "postgres_service" {
  description = "Service do PostgreSQL no cluster"
  value       = "postgres:5432"
}

output "namespace" {
  description = "Namespace da aplicacao"
  value       = var.namespace
}
