variable "cluster_name" {
  description = "Nome do cluster Kind"
  type        = string
  default     = "oficina-cluster"
}

variable "namespace" {
  description = "Namespace Kubernetes para a aplicacao"
  type        = string
  default     = "oficina"
}

variable "postgres_password" {
  description = "Senha do PostgreSQL"
  type        = string
  default     = "oficina123"
  sensitive   = true
}

variable "jwt_secret" {
  description = "Secret do JWT"
  type        = string
  default     = "change-this-secret-in-production"
  sensitive   = true
}

variable "app_image" {
  description = "Imagem Docker da aplicacao"
  type        = string
  default     = "ghcr.io/soat-architecture/tech-challenge-fiap:latest"
}

variable "postgres_storage" {
  description = "Tamanho do volume do PostgreSQL"
  type        = string
  default     = "10Gi"
}
