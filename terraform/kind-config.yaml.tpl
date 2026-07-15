kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: ${cluster_name}
nodes:
  - role: control-plane
    image: kindest/node:${kubernetes_version}
    extraPortMappings:
      - containerPort: ${node_port}
        hostPort: ${node_port}
        listenAddress: "0.0.0.0"
        protocol: TCP
