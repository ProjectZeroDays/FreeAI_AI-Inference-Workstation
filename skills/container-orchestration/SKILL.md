---
name: container-orchestration
description: Kubernetes and container orchestration patterns, deployments, services, ingress, ConfigMaps, Secrets, and Helm charts. Use when the user asks about Kubernetes setup, container orchestration, pod management, service discovery, or Helm chart configuration.
---

# Container Orchestration (Kubernetes)

## Core Resources

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: app
          image: myapp:latest
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 15
            periodSeconds: 20
          envFrom:
            - configMapRef:
                name: myapp-config
            - secretRef:
                name: myapp-secrets
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
  type: ClusterIP
```

### Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp-service
                port:
                  number: 80
```

### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  NODE_ENV: production
  LOG_LEVEL: info
  config.json: |
    {
      "feature_flags": {
        "new_dashboard": true
      }
    }
```

### Secret
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/mydb
  API_KEY: sk_live_abc123
```

## HPA (Horizontal Pod Autoscaler)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

## Persistent Volume

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: myapp-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

## Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: myapp-netpol
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - port: 3000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: database
      ports:
        - port: 5432
```

## Helm Chart

```yaml
# Chart.yaml
apiVersion: v2
name: myapp
version: 1.0.0
dependencies:
  - name: postgresql
    version: 12.x.x
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

```yaml
# values.yaml
replicaCount: 2
image:
  repository: myapp
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: true
  host: myapp.example.com
resources:
  requests:
    memory: 128Mi
    cpu: 250m
  limits:
    memory: 256Mi
    cpu: 500m
```

## Useful Commands

```bash
# Get resources
kubectl get pods -n mynamespace
kubectl get svc,deploy,ing -l app=myapp

# Debug
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous
kubectl exec -it <pod-name> -- /bin/sh

# Scale
kubectl scale deploy/myapp --replicas=5

# Rollout
kubectl rollout status deploy/myapp
kubectl rollout undo deploy/myapp
kubectl rollout history deploy/myapp

# Port forward
kubectl port-forward svc/myapp-service 3000:80

# Apply
kubectl apply -f manifests/
kubectl delete -f manifests/
```

## Namespace Isolation

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    env: production
```

```bash
kubectl config set-context --current --namespace=production
```
