# Infraestrutura como Codigo - Tech Challenge

Este diretorio contem os scripts Terraform para provisionar o ambiente local do projeto.

## O que e provisionado

1. **Cluster Kubernetes local** via Kind (Kubernetes in Docker)
2. **Namespace** `oficina`
3. **ConfigMap** e **Secret** com configuracoes da aplicacao
4. **Banco PostgreSQL** (StatefulSet + PVC de 10Gi)
5. **Deployment** da aplicacao (3 replicas) + Service ClusterIP + HPA

## Pre-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.6

## Como usar

```bash
cd terraform

terraform init
terraform plan
terraform apply -auto-approve

# Opcao A - Port-forward (recomendado para dev)
kubectl port-forward -n oficina svc/oficina-api 8080:80

# Swagger: http://localhost:8080/docs

# Opcao B - NodePort (acesso direto)
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
# Swagger: http://$NODE_IP:30080/docs
```

## Destruir

```bash
terraform destroy -auto-approve
```

## Estrutura dos arquivos

| Arquivo | Descricao |
|---------|-----------|
| `versions.tf` | Providers e versoes |
| `kind.tf` | Criacao do cluster Kind |
| `manifests.tf` | Aplicacao dos manifestos k8s/ |
| `variables.tf` | Variaveis de configuracao |
| `terraform.tfvars` | Valores default |

## Observacoes

- Todo o provisionamento e feito exclusivamente via Terraform (sem comandos `kubectl` manuais).
- Os manifestos em `../k8s/` sao a fonte da verdade -- altere-os diretamente que o Terraform detecta as mudancas.
- O cluster Kind e gerenciado pelo recurso `null_resource` com `local-exec`; nao ha provider Kind dedicado publicado no Registry.
