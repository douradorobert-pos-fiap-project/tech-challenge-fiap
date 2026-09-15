# Sistema Integrado de Atendimento e Execução de Servicos - Oficina Mecanica

Sistema back-end para gestao de ordens de servico, clientes e pecas de oficina mecanica, aplicando Arquitetura Hexagonal (Clean Architecture), boas praticas de Qualidade de Software e Seguranca.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12+ |
| Framework | FastAPI |
| Gerenciamento de deps | Poetry |
| Banco prod | PostgreSQL RDS (AWS) |
| Testes | Pytest + pytest-cov + pytest-mock |
| Auth | JWT (bcrypt + python-jose) |
| Container | Docker |
| Orquestracao | Kubernetes (EKS) |
| IaC | Terraform |
| CI/CD | GitHub Actions |
| Lambda | CPF Validator (AWS Lambda) |

## Arquitetura Hexagonal (Ports & Adapters)

```
Domain (puro, sem deps técnicas)
  ↓
Application (use cases + ports)
  ↓
Infrastructure (adapters: DB, auth, email, Lambda)
  ↓
API (FastAPI routes - adapter de entrada)
```

## Execução Local

### Pré-requisitos

- Python 3.12+
- Poetry
- Docker e docker-compose
- AWS CLI (para deploy)

### Configuração

1. Copie o arquivo `.env.example` para `.env` e ajuste as variáveis:

```bash
cp .env.example .env
```

2. As variáveis essenciais são:

```env
DATABASE_URL=postgresql://oficina_admin:oficina123@localhost:5432/oficina
JWT_SECRET=sua-chave-secreta
CPF_VALIDATOR_LAMBDA_ARN=arn:aws:lambda:us-east-1:SEU_ACCOUNT:function:CpfValidatorTest
```

### Desenvolvimento

Para rodar localmente com docker-compose (banco local):

```bash
docker-compose -f docker-compose.dev.yml up --build
```

A API estará disponível em `http://localhost:8000/docs`

### Testes

```bash
poetry install
poetry run pytest
```

### Build da Imagem

```bash
docker build -t tech-challenge-app .
```

## Deploy na AWS

### Infraestrutura

O deploy utiliza infraestrutura já provisionada:

- **EKS Cluster**: `sandbox-eks` (via `shared-infra`)
- **RDS PostgreSQL**: `sandbox-oficina-postgresql` (via `database-infra`)
- **Lambda CPF Validator**: `CpfValidatorTest` (via `tech-challenge-fiap-lambda`)
- **ECR**: `application` (via `shared-infra`)
- **API Gateway + NLB**: (via `shared-infra`)

### Pipeline CI/CD

O pipeline GitHub Actions executa:

1. **Validate**: Lint (black, isort) + testes pytest com cobertura
2. **Build and Push**: Build da imagem Docker + push para ECR
3. **Deploy**: Atualização dos manifests K8s + deploy no EKS

### Variáveis Necessárias no GitHub Actions

O pipeline lê a maior parte dos valores diretamente do **terraform state** no S3 e do **Secrets Manager**, minimizando a configuração manual.

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

| Secret | Descrição |
|--------|-----------|
| `AWS_ACCESS_KEY_ID` | Access key da conta AWS |
| `AWS_SECRET_ACCESS_KEY` | Secret access key |
| `AWS_SESSION_TOKEN` | Token da sessão temporária |
| `DB_PASSWORD` | Senha do PostgreSQL RDS |
| `SMTP_USER` | Usuário SMTP (opcional) |
| `SMTP_PASSWORD` | Senha SMTP (opcional) |

**Valores lidos automaticamente pelo pipeline:**

| Valor | Fonte |
|-------|-------|
| `rds_endpoint`, `database_username`, `database_name` | Terraform state do `database-infra` |
| `eks_cluster_name`, `ecr_repository_url`, `lambda_arn`, `eks_node_role_arn` | Terraform state do `shared-infra` |
| `target_group_arn` | AWS CLI (ELBv2) |
| `vpc_link_sg_id` | AWS CLI (EC2) |
| `jwt_secret` | AWS Secrets Manager (`sandbox/jwt-secret`) |

### Permissões IAM

A IAM Role utilizada pelos pods EKS precisa da seguinte permissão:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-east-1:*:function:CpfValidatorTest"
    }
  ]
}
```

## Estrutura do Projeto

```
src/
├── api/                    # FastAPI routes (adapter de entrada)
│   ├── main.py            # App FastAPI
│   ├── routes/            # Rotas HTTP
│   └── dependencies.py    # Injeção de dependências
├── application/           # Casos de uso + ports
│   ├── dtos/              # Data Transfer Objects
│   ├── ports/             # Interfaces (repositórios, externo)
│   └── usecases/          # Lógica de negócio
├── domain/                # Entidades e regras de negócio
│   ├── entities/          # Modelos de domínio
│   ├── exceptions/        # Exceções de domínio
│   ├── services/          # Serviços de domínio
│   └── value_objects/     # Objetos de valor (CPF, Email, etc)
└── infrastructure/        # Implementações técnicas
    ├── adapters/          # Adaptadores (email, Lambda CPF)
    ├── auth/              # JWT handler
    ├── config/            # Settings (pydantic-settings)
    └── database/          # SQLAlchemy models e repositories

k8s/                       # Manifests Kubernetes
├── namespace.yaml
├── configmap.yaml
├── secret.yaml
├── deployment.yaml
├── service.yaml
├── service-account.yaml
├── hpa.yaml
├── migration-job.yaml
└── target-group-binding.yaml
```

## Dependências dos Repositórios de Infraestrutura

Este repositório depende de recursos já provisionados:

1. **shared-infra**: EKS cluster, ECR, NLB, API Gateway, Secrets Manager (JWT)
2. **database-infra**: PostgreSQL RDS
3. **tech-challenge-fiap-lambda**: Lambda CPF Validator

### Terraform State no S3

O pipeline lê os outputs dos estados do Terraform salvos no S3:

| Bucket | Key | Outputs utilizados |
|--------|-----|-------------------|
| `terraform-state-264040538379-us-east-1` | `sandbox/terraform.tfstate` | `eks_cluster_name`, `ecr_application_repository_url`, `lambda_arn`, `eks_node_role_arn` |
| `terraform-state-264040538379-us-east-1` | `database/terraform.tfstate` | `rds_endpoint`, `rds_port`, `database_name`, `database_username` |

### Recursos AWS acessados via CLI

| Recurso | Método AWS CLI |
|---------|---------------|
| NLB Target Group | `aws elbv2 describe-target-groups --names sandbox-app-tg` |
| VPC Link Security Group | `aws ec2 describe-security-groups --filters "Name=group-name,Values=sandbox-vpclink-*"` |
| JWT Secret | `aws secretsmanager get-secret-value --secret-id sandbox/jwt-secret` |

## Documentação Adicional

- [Documentação da API Gateway](../shared-infra/docs/api-gateway-routes.md)
