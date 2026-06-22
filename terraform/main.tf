resource "kubernetes_namespace" "oficina" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/name" = "oficina"
    }
  }
}

resource "kubernetes_config_map" "oficina_config" {
  metadata {
    name      = "oficina-config"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  data = {
    APP_NAME              = "Sistema de Oficina"
    APP_VERSION           = "1.0.0"
    APP_ENV               = "production"
    DATABASE_URL          = "postgresql://oficina:${var.postgres_password}@postgres:5432/oficina"
    JWT_ALGORITHM         = "HS256"
    JWT_EXPIRATION_MINUTES = "60"
    SMTP_HOST             = "smtp.gmail.com"
    SMTP_PORT             = "587"
    SMTP_FROM             = "noreply@oficina.com"
  }
}

resource "kubernetes_secret" "oficina_secrets" {
  metadata {
    name      = "oficina-secrets"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  data = {
    JWT_SECRET   = base64encode(var.jwt_secret)
    DB_PASSWORD  = base64encode(var.postgres_password)
    SMTP_USER    = base64encode("your-smtp-user@gmail.com")
    SMTP_PASSWORD = base64encode("your-app-password")
  }
  type = "Opaque"
}

resource "kubernetes_persistent_volume_claim" "postgres_pvc" {
  metadata {
    name      = "postgres-pvc"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    access_modes = ["ReadWriteOnce"]
    resources {
      requests = {
        storage = var.postgres_storage
      }
    }
  }
}

resource "kubernetes_stateful_set" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    service_name = "postgres"
    replicas     = 1
    selector {
      match_labels = {
        "app.kubernetes.io/name"      = "oficina"
        "app.kubernetes.io/component" = "postgres"
      }
    }
    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"      = "oficina"
          "app.kubernetes.io/component" = "postgres"
        }
      }
      spec {
        container {
          name  = "postgres"
          image = "postgres:16-alpine"
          port {
            name           = "postgres"
            container_port = 5432
          }
          env {
            name  = "POSTGRES_DB"
            value = "oficina"
          }
          env {
            name  = "POSTGRES_USER"
            value = "oficina"
          }
          env {
            name = "POSTGRES_PASSWORD"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.oficina_secrets.metadata[0].name
                key  = "DB_PASSWORD"
              }
            }
          }
          volume_mount {
            name       = "postgres-data"
            mount_path = "/var/lib/postgresql/data"
          }
        }
        volume {
          name = "postgres-data"
          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.postgres_pvc.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "postgres" {
  metadata {
    name      = "postgres"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    type = "ClusterIP"
    port {
      port        = 5432
      target_port = "postgres"
    }
    selector = {
      "app.kubernetes.io/name"      = "oficina"
      "app.kubernetes.io/component" = "postgres"
    }
  }
}

resource "kubernetes_deployment" "api" {
  metadata {
    name      = "oficina-api"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    replicas = 3
    selector {
      match_labels = {
        "app.kubernetes.io/name"      = "oficina"
        "app.kubernetes.io/component" = "api"
      }
    }
    template {
      metadata {
        labels = {
          "app.kubernetes.io/name"      = "oficina"
          "app.kubernetes.io/component" = "api"
        }
      }
      spec {
        container {
          name  = "api"
          image = var.app_image
          port {
            name           = "http"
            container_port = 8000
          }
          env_from {
            config_map_ref {
              name = kubernetes_config_map.oficina_config.metadata[0].name
            }
          }
          env_from {
            secret_ref {
              name = kubernetes_secret.oficina_secrets.metadata[0].name
            }
          }
          liveness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            initial_delay_seconds = 10
            period_seconds        = 30
          }
          readiness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "api" {
  metadata {
    name      = "oficina-api"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    type = "NodePort"
    port {
      port        = 80
      target_port = "http"
      node_port   = 30080
    }
    selector = {
      "app.kubernetes.io/name"      = "oficina"
      "app.kubernetes.io/component" = "api"
    }
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "api_hpa" {
  metadata {
    name      = "oficina-api-hpa"
    namespace = kubernetes_namespace.oficina.metadata[0].name
  }
  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment.api.metadata[0].name
    }
    min_replicas = 2
    max_replicas = 10
    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }
    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}
