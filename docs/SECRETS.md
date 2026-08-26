# Secrets Management

Two supported modes (both work; pick one):

## 1. SOPS + Age (default, no server)
Secrets live in `config/secrets.enc.yaml` (age-encrypted). Decrypt at runtime:

``bash
sops exec-env config/secrets.enc.yaml 'docker compose up'
# or systemd: sops exec-env ... systemctl start freeai-stack
``

Rotate: `age-keygen` ? update `.sops.yaml` recipient ? `sops updatekeys config/secrets.enc.yaml`.

## 2. Vault + Kubernetes Secrets
For K8s, use External Secrets Operator or Sealed Secrets:

``bash
kubectl create secret generic freeai-router --from-literal=api_key=... --dry-run=client -o yaml | kubeseal -o yaml > k8s/sealed-router-secret.yml
# or Vault Agent Injector annotation on the Deployment
``

Vault path: `secret/freeai/router` ? `ROUTER_API_KEY`.

Both modes are documented; SOPS is zero-infra and works today, Vault is for team K8s.
