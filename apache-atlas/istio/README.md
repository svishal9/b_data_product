# Istio Resources (Minikube + Cluster)

Atlas is exposed through Istio on port `23000`.

## Layout

- `base/`: shared Istio resources (`Gateway`, `VirtualService`, ingress Service)
- `overlays/minikube/`: patches ingress Service to `NodePort`
- `overlays/cluster/`: patches ingress Service to `LoadBalancer`

## Deploy

Use the parent script:

```bash
cd ..
./deploy.sh minikube
./deploy.sh cluster
```

Or apply overlays manually after Istio is installed:

```bash
kubectl apply -k istio/overlays/minikube
kubectl apply -k istio/overlays/cluster
```

## Access

- Minikube:

```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000
```

- Cluster (LoadBalancer): use external IP from:

```bash
kubectl get svc -n istio-system istio-ingressgateway-atlas
```

