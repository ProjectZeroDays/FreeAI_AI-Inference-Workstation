# Advanced Path — GPU Tuning, Custom Agents & Cloud

For operators who want maximum performance and custom integrations.

## Step 1: GPU Power Tuning

```bash
# Check current power state
nvidia-smi --query-gpu=power.draw,power.limit,clocks.current,clocks.max --format=csv

# Apply eco profile (lower power, lower clock)
sudo ./hardware/gpu-power-tune.sh apply eco

# Check status
sudo ./hardware/gpu-power-tune.sh status

# Reset to stock
sudo ./hardware/gpu-power-tune.sh reset
```

## Step 2: Write a Custom Agent

Create `agents/custom/my_agent.py`:

```python
from agents.base import BaseAgent

class MyAgent(BaseAgent):
    name = "my_agent"
    role = "general"

    async def run(self, context: dict) -> dict:
        prompt = context.get("prompt", "")
        # Your logic here
        return {"result": "done", "output": "..." }
```

Register in `config/agents.json`:
```json
{"my_agent": {"path": "agents/custom/my_agent.py", "enabled": true}}
```

## Step 3: Deploy to Cloud GPU

```bash
# Vast.ai template
template env PROVISIONING_SCRIPT=<release bundle URL>

# RunPod — use GHCR all-in-one image
docker pull ghcr.io/projectzerodays/freeai-allinone:latest

# Kubernetes
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/models-pvc.yml
kubectl apply -f k8s/
```

## Step 4: Security Hardening

```bash
# Set API keys
export ROUTER_API_KEY=your-router-key
export AGENT_API_KEY=your-agent-key
export AUTONOMOUS_API_KEY=your-autonomous-key

# Enable UFW (included in install-stack.sh)
sudo ufw allow 22/tcp
sudo ufw allow 8030/tcp
sudo ufw allow 8050/tcp
sudo ufw enable
```

## Step 5: Backup & Restore

```bash
# Create backup
bash scripts/backup.sh

# List backups
bash scripts/backup.sh list

# Restore
bash scripts/backup.sh restore backups/backup-20260903.tar.gz
```
