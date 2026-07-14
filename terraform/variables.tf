variable "cluster_name" {
  description = "Nome do cluster Kind"
  type        = string
  default     = "tech-challenge"
}

variable "kubernetes_version" {
  description = "Versao do Kubernetes no Kind"
  type        = string
  default     = "v1.31.0"
}

variable "kind_node_image" {
  description = "Imagem do node Kind"
  type        = string
  default     = null
}

variable "ghcr_username" {
  description = "Usuario do GitHub Container Registry"
  type        = string
}

variable "ghcr_pat" {
  description = "Personal Access Token do GitHub com escopo write:packages"
  type        = string
  sensitive   = true
}
