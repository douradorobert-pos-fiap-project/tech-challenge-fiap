# Sistema Integrado de Atendimento e Execução de Servicos - Oficina Mecanica

Sistema back-end para gestao de ordens de servico, clientes e pecas de oficina mecanica, aplicando Arquitetura Hexagonal (Clean Architecture), boas praticas de Qualidade de Software e Seguranca.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Linguagem | Python 3.12+ |
| Framework | FastAPI |
| Gerenciamento de deps | Poetry |
| Banco dev | SQLite |
| Banco prod | PostgreSQL |
| Testes | Pytest + pytest-cov + pytest-mock |
| Auth | JWT (bcrypt + python-jose) |
| Container | Docker + docker-compose |
| Orquestracao | Kubernetes (Kind) |
| IaC | Terraform |
| CI/CD | GitHub Actions |

## Arquitetura Hexagonal (Ports & Adapters)

```
Domain (puro, sem deps técnicas)
  ↓
Application (use cases + ports)
  ↓
Infrastructure (adapters: DB, auth, email)
  ↓
API (FastAPI routes - adapter de entrada)
```

- **Domain**: Entidades, Value Objects, servicos de dominio, excecoes
- **Application**: Casos de uso, DTOs, Ports (interfaces)
- **Infrastructure**: Repositorios SQLAlchemy, JWT handler, email adapter
- **API**: Rotas FastAPI, middleware, composition root

## Estrutura do Projeto

```
src/
├── domain/           # Entidades, VOs, servicos de dominio
├── application/      # Use cases, DTOs, Ports
├── infrastructure/   # Repositorios, auth, config, adapters
├── api/              # Rotas FastAPI, dependencies
├── migrations/       # Alembic migrations
└── alembic.ini       # Configuracao do Alembic
tests/
├── unit/             # Testes do dominio e aplicacao
└── integration/      # Testes da API
k8s/                  # Manifestos Kubernetes
terraform/            # Infraestrutura como Codigo
.github/workflows/    # CI/CD
docker/               # Dockerfile
```

## Como Executar Localmente

### Opcao 1: Poetry (desenvolvimento)

```bash
# Instalar dependencias
poetry install

# Copiar .env
cp .env.example .env

# Executar migracoes do banco
poetry run alembic upgrade head

# Executar aplicacao
poetry run uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Acessar documentacao Swagger
# http://localhost:8000/docs
```

### Opcao 2: Docker Compose

```bash
# Build e execução
docker compose up --build

# Executar migracoes do banco (uma vez)
docker compose run --rm app alembic -c /app/alembic.ini upgrade head

# Acessar: http://localhost:8000/docs
```

> Para usar PostgreSQL, utilize `docker compose.dev.yml`: `docker compose -f docker-compose.dev.yml up --build`

### Opcao 3: Kubernetes + Terraform

```bash
cd terraform
terraform init
terraform apply -auto-approve

# Port-forward para acessar
kubectl port-forward -n oficina svc/oficina-api 8080:80
# Acessar: http://localhost:8080/docs
```

## Credenciais de Acesso

- **Usuario**: admin
- **Senha**: secret

## APIs Disponiveis

### Autenticacao (JWT)
- `POST /api/v1/auth/login` - Login e obtencao do token JWT

### APIs Administrativas (JWT obrigatorio)
- `POST/GET/PUT/DELETE /api/v1/clientes` - CRUD de clientes
- `POST/GET/PUT/DELETE /api/v1/veiculos` - CRUD de veiculos
- `POST/GET/PUT/DELETE /api/v1/servicos` - CRUD de servicos do catalogo
- `POST/GET/PUT/PATCH/DELETE /api/v1/pecas` - CRUD de pecas + controle de estoque
- `POST /api/v1/ordens-servico` - Abertura de OS
- `GET /api/v1/ordens-servico` - Listagem de OS (ordenada por status + mais antigas primeiro; exclui finalizadas/entregues)
- `GET /api/v1/ordens-servico/{id}` - Detalhamento de OS
- `PATCH /api/v1/ordens-servico/{id}/status` - Atualizacao de status
- `POST /api/v1/ordens-servico/{id}/orcamento/aprovar` - Aprovacao/recusa de orcamento (endpoint publico para notificacoes externas)

### APIs Publicas (sem JWT)
- `GET /api/v1/public/ordens-servico/{id}/status` - Consulta publica do status da OS

### Ordenacao de Listagem de OS

A listagem de OS segue a seguinte ordem de prioridade:
1. Em Execucao
2. Aguardando Aprovacao
3. Diagnostico
4. Recebida

Dentro de cada status, as OS mais antigas aparecem primeiro. OS finalizadas e entregues sao excluidas (soft-delete logico).

## Testes

```bash
# Todos os testes
poetry run pytest

# Apenas testes unitarios
poetry run pytest tests/unit/

# Apenas testes de integracao
poetry run pytest tests/integration/

# Com cobertura
poetry run pytest --cov=src --cov-report=html --cov-fail-under=80
# Abrir htmlcov/index.html
```

### Cobertura atual: 85%+ nos dominios criticos

## CI/CD

### Pipeline de CI (`.github/workflows/ci.yml`)
- Lint (Ruff)
- Testes automatizados com cobertura minima de 80%
- Build da imagem Docker
- Smoke test do container

### Pipeline de CD (`.github/workflows/cd.yml`)
- Build e push da imagem para GitHub Container Registry
- Provisionamento do cluster Kubernetes via Terraform (Kind)
- Deploy do PostgreSQL (StatefulSet)
- Deploy da aplicacao (Deployment + HPA)
- Aplicacao dos manifestos YAML
- Smoke test no cluster

## Justificativa do Banco de Dados

- **SQLite (dev)**: Leve, sem necessidade de servidor, ideal para desenvolvimento rapido e testes em memoria.
- **PostgreSQL (prod)**: Robusto, ACID, com suporte a JSON, particionamento e replicacao. Ideal para o dominio de OS/estoque/clientes que exige integridade referencial e transacoes confiaveis.

## Validacoes Implementadas

- **CPF/CNPJ**: Validacao de digitos verificadores (modulo 11)
- **Placa**: Suporte a formato Mercosul (AAA1A11) e antiga (AAA1111)
- **Email**: Validacao de formato RFC
- **Dinheiro**: Impede valores negativos, arredondamento de 2 casas
- **Maquina de estados da OS**: Transicoes validadas (Recebida -> Diagnostico -> Aguardando Aprovacao -> Em Execucao -> Finalizada -> Entregue)

## Licenca

MIT
