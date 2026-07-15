resource "local_file" "kind_config" {
  content = templatefile("${path.module}/kind-config.yaml.tpl", {
    cluster_name       = var.cluster_name
    kubernetes_version = var.kubernetes_version
    node_port          = var.node_port
  })
  filename = "${path.module}/.kind-config.yaml"
}

resource "null_resource" "kind_cluster" {
  triggers = {
    cluster_name       = var.cluster_name
    kubernetes_version = var.kubernetes_version
    node_port          = var.node_port
    config_hash        = local_file.kind_config.content_md5
  }

  provisioner "local-exec" {
    command = <<-EOT
      kind create cluster \
        --config ${local_file.kind_config.filename} \
        --wait 120s
      kubectl config use-context kind-${var.cluster_name}
    EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      kind delete cluster --name ${self.triggers.cluster_name}
    EOT
  }
}

resource "terraform_data" "kind_ready" {
  depends_on = [null_resource.kind_cluster]

  provisioner "local-exec" {
    command = <<-EOT
      echo "Aguardando cluster Kind ficar acessivel..."
      i=1
      while [ $i -le 30 ]; do
        if kubectl cluster-info --context=${local.kube_context} > /dev/null 2>&1; then
          echo "Cluster pronto!"
          exit 0
        fi
        echo "Tentativa $i/30 - aguardando..."
        i=$((i + 1))
        sleep 2
      done
      echo "Cluster nao respondeu apos 60 segundos"
      exit 1
    EOT
  }
}
