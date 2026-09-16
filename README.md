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

```mermaid
flowchart LR
    client[Cliente HTTP] --> gateway[API Gateway de shared-infra]
    gateway -->|VPC Link e NLB| service[Service Kubernetes no EKS]
    service --> api[Rotas FastAPI]
    api --> usecases[Casos de uso e ports]
    usecases --> domain[Entidades e regras de domínio]
    usecases --> adapters[Adapters de infraestrutura]
    adapters -->|SQLAlchemy/Alembic| rds[(RDS PostgreSQL de database-infra)]
    adapters -->|Invocação AWS| cpf[Lambda CPF Validator]
    adapters -->|JWT e email| external[Autenticação e SMTP]
```

O código de domínio não depende dos adapters. Este repositório contém a API, as regras de negócio, as migrations e os manifests da aplicação; os recursos AWS compartilhados são provisionados pelos outros repositórios.

## Execução Local

### Pré-requisitos

- Python 3.12+
- Poetry
- Docker com Compose
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

Para rodar localmente com Docker Compose e banco local:

```bash
docker compose -f docker-compose.dev.yml up --build
```

A API estará disponível em `http://localhost:8000/docs`

### Documentação da API

- [Swagger UI da API local](http://localhost:8000/docs) — disponível após iniciar o Compose ou o Uvicorn.
- [OpenAPI JSON da API local](http://localhost:8000/openapi.json) — especificação gerada pelo FastAPI.

O API Gateway de produção tem endpoint variável por ambiente (`api_gateway_endpoint` em `shared-infra`). As rotas `/docs` e `/openapi.json` não estão configuradas no Gateway; para consultar o Swagger da instância implantada, acesse a API pela rede do cluster, por exemplo com `kubectl port-forward -n oficina service/oficina-api 8000:80`, e abra os links locais acima. Não há coleção Postman versionada neste repositório.

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

- [Documentação da API Gateway](https://github.com/douradorobert-pos-fiap-project/shared-infra/blob/main/docs/api-gateway-routes.md)


## Monitoring and Observability

A aplicacao usa o agente oficial New Relic para Python, com auto-instrumentacao de FastAPI/Uvicorn, SQLAlchemy e chamadas suportadas. O agente e inicializado somente quando `NEW_RELIC_LICENSE_KEY` existe; sem ela, a aplicacao e os testes funcionam normalmente. Distributed tracing fica habilitado por `NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true`.

Variaveis de ambiente:

- `NEW_RELIC_LICENSE_KEY`: Secret do New Relic; nunca inclua seu valor no codigo, imagem, manifests versionados ou testes.
- `NEW_RELIC_APP_NAME`: nome exibido no APM (no Kubernetes: `oficina-api`).
- `NEW_RELIC_ENVIRONMENT`: ambiente do agente (no Kubernetes: `production`).
- `NEW_RELIC_DISTRIBUTED_TRACING_ENABLED`: habilita tracing distribuido.

O pipeline adiciona `NEW_RELIC_LICENSE_KEY` ao Secret Kubernetes `oficina-secrets`, usando o GitHub Actions Secret de mesmo nome. Nao e necessario Helm ou agente adicional de coleta de logs.

### Logs, correlation ID e healthchecks

Logs sao JSON em stdout, com `timestamp`, `level`, `message`, `service`, `environment`, `correlation_id` e, para requests, `request_method`, `request_path`, `status_code` e `duration_ms`. JWT, Authorization, senhas, secrets e payloads de CPF nao sao registrados.

Cada request reutiliza `X-Correlation-ID` recebido (limitado a 128 caracteres) ou gera UUID; o mesmo valor e retornado em `X-Correlation-ID`. Nao ha cliente HTTP proprio na aplicacao para propagar o header. O agente New Relic propaga contexto de tracing automaticamente em bibliotecas suportadas.

`/health` e o healthcheck existente e e usado por liveness, readiness e startup probes. A liveness nao depende do banco ou da Lambda.

Validacao local:

```bash
NEW_RELIC_APP_NAME=oficina-api NEW_RELIC_ENVIRONMENT=development \
  uvicorn src.api.main:app --reload
curl -i http://localhost:8000/health
curl -i -H 'X-Correlation-ID: local-check-123' http://localhost:8000/health
```

Depois do deploy, confirme o rollout e consulte logs:

```bash
kubectl rollout status deployment/oficina-api -n oficina
kubectl logs -n oficina deployment/oficina-api
kubectl logs -n oficina deployment/oficina-api | grep '"correlation_id":"local-check-123"'
```

No New Relic, abra APM & Services e selecione `oficina-api`; use Distributed tracing para requests e chamadas externas. Os eventos customizados sao `ServiceOrderCreated`, `ServiceOrderStatusChanged`, `ServiceOrderStatusDuration` e `IntegrationError`.

### NRQL para dashboards

As consultas abaixo usam exatamente os eventos emitidos pela aplicacao:

```sql
-- Latencia, throughput e taxa de erros HTTP (APM)
SELECT average(duration), percentile(duration, 95)
FROM Transaction
WHERE appName = 'oficina-api'
TIMESERIES

SELECT rate(count(*), 1 minute)
FROM Transaction
WHERE appName = 'oficina-api'
TIMESERIES

SELECT percentage(count(*), WHERE error IS TRUE)
FROM Transaction
WHERE appName = 'oficina-api'
TIMESERIES

-- Volume diario de OS
SELECT count(*)
FROM ServiceOrderCreated
FACET status
TIMESERIES 1 day

-- Tempo emitido ao sair dos status relevantes
SELECT average(duration_ms)
FROM ServiceOrderStatusDuration
WHERE status IN ('DIAGNOSTICO', 'EM_EXECUCAO', 'FINALIZADA')
FACET status
TIMESERIES

-- Falhas das integracoes
SELECT count(*)
FROM IntegrationError
FACET integration, operation, error_type
TIMESERIES
```

O evento de duracao e emitido na transicao de saida e usa `atualizada_em` como inicio. O modelo atual nao possui historico de status; portanto, nao e possivel reconstruir retrospectivamente tempos por status nem medir corretamente o primeiro status criado quando nao houve intervalo observavel. Uma tabela de historico seria necessaria para essa precisao, mas nao foi introduzida para manter a mudanca incremental.
