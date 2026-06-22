# Terraform - Infraestrutura como Código

Este diretório contém os scripts Terraform para provisionamento do cluster Kubernetes (Kind) e do banco de dados PostgreSQL.

## Recursos Criados

| Recurso | Descrição |
|---------|-----------|
| `kind_cluster` | Cluster Kubernetes local usando Kind (1 control-plane + 1 worker) |
| `kubernetes_namespace` | Namespace `oficina` para isolar os recursos |
| `kubernetes_config_map` | Variáveis de configuração não-sensíveis |
| `kubernetes_secret` | Variáveis sensíveis (JWT secret, DB password, SMTP credentials) |
| `kubernetes_persistent_volume_claim` | Volume persistente de 10Gi para PostgreSQL |
| `kubernetes_stateful_set` | StatefulSet do PostgreSQL 16 |
| `kubernetes_service (postgres)` | Service ClusterIP para acesso ao PostgreSQL |
| `kubernetes_deployment` | Deployment da aplicação (3 réplicas) |
| `kubernetes_service (api)` | Service NodePort para acesso à API (porta 30080 → localhost:8080) |
| `kubernetes_horizontal_pod_autoscaler` | HPA escalando de 2 a 10 pods (CPU 70%, memória 80%) |

## Pré-requisitos

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5.0
- [Docker](https://docs.docker.com/get-docker/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) instalado

## Como Aplicar

```bash
# 1. Inicializar o Terraform
terraform init

# 2. Visualizar o plano de execução
terraform plan

# 3. Aplicar a infraestrutura
terraform apply -auto-approve

# 4. Configurar kubectl para acessar o cluster
kind get kubeconfig --name oficina-cluster > ~/.kube/config-oficina
export KUBECONFIG=~/.kube/config-oficina

# 5. Verificar os pods
kubectl get pods -n oficina

# 6. Acessar a API
# Via port-forward:
kubectl port-forward -n oficina svc/oficina-api 8080:80
# Acesse: http://localhost:8080/docs
```

## Variáveis

| Variável | Descrição | Default |
|----------|-----------|---------|
| `cluster_name` | Nome do cluster Kind | `oficina-cluster` |
| `namespace` | Namespace Kubernetes | `oficina` |
| `postgres_password` | Senha do PostgreSQL | `oficina123` |
| `jwt_secret` | Secret do JWT | `change-this-secret-in-production` |
| `app_image` | Imagem Docker da aplicação | `ghcr.io/soat-architecture/tech-challenge-fiap:latest` |
| `postgres_storage` | Tamanho do volume do PostgreSQL | `10Gi` |

## Destruir

```bash
terraform destroy -auto-approve
```
