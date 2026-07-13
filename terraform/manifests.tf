locals {
  k8s_dir      = "${path.module}/../k8s"
  kube_context = "kind-${var.cluster_name}"
  ghcr_auth    = base64encode("${var.ghcr_username}:${var.ghcr_pat}")
  ghcr_dockerconfig = jsonencode({
    auths = {
      "ghcr.io" = {
        username = var.ghcr_username
        password = var.ghcr_pat
        auth     = local.ghcr_auth
      }
    }
  })
  ghcr_secret_yaml = yamlencode({
    apiVersion = "v1"
    kind       = "Secret"
    metadata = {
      name      = "ghcr-secret"
      namespace = "oficina"
    }
    type = "kubernetes.io/dockerconfigjson"
    data = {
      ".dockerconfigjson" = base64encode(local.ghcr_dockerconfig)
    }
  })
  secret_yaml = yamlencode({
    apiVersion = "v1"
    kind       = "Secret"
    metadata = {
      name      = "oficina-secrets"
      namespace = "oficina"
      labels = {
        "app.kubernetes.io/name" = "oficina"
      }
    }
    type = "Opaque"
    data = {
      JWT_SECRET    = base64encode("CHANGE-ME-IN-PRODUCTION")
      DB_PASSWORD   = base64encode("oficina123")
      SMTP_USER     = base64encode("your-smtp-user@gmail.com")
      SMTP_PASSWORD = base64encode("your-app-password")
    }
  })
}

resource "null_resource" "k8s_namespace" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/namespace.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/namespace.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/namespace.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [terraform_data.kind_ready]
}

resource "null_resource" "k8s_configmap" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/configmap.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/configmap.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/configmap.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_namespace]
}

resource "null_resource" "k8s_secret" {
  triggers = {
    inline       = md5(local.secret_yaml)
    yaml_b64     = base64encode(local.secret_yaml)
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "echo ${self.triggers.yaml_b64} | base64 -d | kubectl apply -f - --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete secret oficina-secrets -n oficina --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_namespace]
}

resource "null_resource" "k8s_ghcr_secret" {
  triggers = {
    inline       = md5(local.ghcr_secret_yaml)
    yaml_b64     = base64encode(local.ghcr_secret_yaml)
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "echo ${self.triggers.yaml_b64} | base64 -d | kubectl apply -f - --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete secret ghcr-secret -n oficina --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_namespace]
}

resource "null_resource" "k8s_postgres_pvc" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/postgres-pvc.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/postgres-pvc.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/postgres-pvc.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_namespace]
}

resource "null_resource" "k8s_postgres_statefulset" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/postgres-statefulset.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/postgres-statefulset.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/postgres-statefulset.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [
    null_resource.k8s_postgres_pvc,
    null_resource.k8s_secret,
  ]
}

resource "null_resource" "k8s_postgres_service" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/postgres-service.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/postgres-service.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/postgres-service.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_postgres_statefulset]
}

resource "null_resource" "k8s_deployment" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/deployment.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/deployment.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/deployment.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [
    null_resource.k8s_configmap,
    null_resource.k8s_secret,
    null_resource.k8s_ghcr_secret,
    null_resource.k8s_postgres_statefulset,
  ]
}

resource "null_resource" "k8s_service" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/service.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/service.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/service.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_deployment]
}

resource "null_resource" "k8s_hpa" {
  triggers = {
    yaml         = filemd5("${local.k8s_dir}/hpa.yaml")
    k8s_dir      = local.k8s_dir
    kube_context = local.kube_context
  }

  provisioner "local-exec" {
    command = "kubectl apply -f ${self.triggers.k8s_dir}/hpa.yaml --context=${self.triggers.kube_context}"
  }

  provisioner "local-exec" {
    when    = destroy
    command = "kubectl delete -f ${self.triggers.k8s_dir}/hpa.yaml --context=${self.triggers.kube_context} --ignore-not-found"
  }

  depends_on = [null_resource.k8s_deployment]
}
