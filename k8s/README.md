# Apex Kubernetes Manifests

These manifests use Kustomize overlays. Do not apply an overlay directory with
`kubectl apply -f k8s/overlays/local/`; that treats `kustomization.yaml` as a
Kubernetes custom resource and requires a Kustomization CRD.

Use one of these forms instead:

```bash
# Render and inspect local manifests.
kustomize build k8s/overlays/local

# Client-side dry run.
kubectl apply --dry-run=client -k k8s/overlays/local

# Equivalent explicit render/apply pipeline.
kustomize build k8s/overlays/local | kubectl apply --dry-run=client -f -

# Apply to a cluster.
kubectl apply -k k8s/overlays/local
```

Production follows the same pattern with `k8s/overlays/production`.
