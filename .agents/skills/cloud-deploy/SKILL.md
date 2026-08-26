---
name: cloud-deploy
description: Cloud deployment strategies for AWS, GCP, and Azure, including containerized deployments, serverless, and infrastructure patterns. Use when the user asks about deploying to cloud platforms, setting up cloud infrastructure, serverless functions, or cloud-specific configurations.
---

# Cloud Deployment

## AWS ECS (Container Service)

```json
// task-definition.json
{
  "family": "myapp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:latest",
      "portMappings": [
        { "containerPort": 3000, "protocol": "tcp" }
      ],
      "environment": [
        { "name": "NODE_ENV", "value": "production" }
      ],
      "secrets": [
        { "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:..." }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/myapp",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# Deploy
aws ecs update-service --cluster mycluster --service myapp --force-new-deployment

# Scale
aws ecs update-service --cluster mycluster --service myapp --desired-count 3
```

## AWS Lambda (Serverless)

```yaml
# serverless.yml (Serverless Framework)
service: my-api

provider:
  name: aws
  runtime: nodejs20.x
  region: us-east-1
  environment:
    TABLE_NAME: ${self:service}-${sls:stage}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource: !GetAtt Table.Arn

functions:
  getUser:
    handler: src/handlers/getUser.handler
    events:
      - http:
          path: /users/{id}
          method: get

  createUser:
    handler: src/handlers/createUser.handler
    events:
      - http:
          path: /users
          method: post

resources:
  Resources:
    Table:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${sls:stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: id
            AttributeType: S
        KeySchema:
          - AttributeName: id
            KeyType: HASH
```

## AWS CDK (Infrastructure as Code)

```typescript
import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as elbv2 from 'aws-cdk-lib/aws-elasticloadbalancingv2';

export class AppStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2 });

    const cluster = new ecs.Cluster(this, 'Cluster', {
      vpc,
      containerInsights: true,
    });

    const service = new ecs.FargateService(this, 'Service', {
      cluster,
      desiredCount: 2,
      taskDefinition,
    });

    const lb = new elbv2.ApplicationLoadBalancer(this, 'LB', {
      vpc,
      internetFacing: true,
    });

    const listener = lb.addListener('Listener', { port: 80 });
    listener.addTargets('Target', {
      port: 3000,
      targets: [service],
      healthCheck: { path: '/health' },
    });
  }
}
```

## Vercel (Frontend/Serverless)

```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.js",
      "use": "@vercel/node"
    },
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/$1" },
    { "handle": "filesystem" },
    { "src": "/(.*)", "dest": "/index.html" }
  ],
  "env": {
    "DATABASE_URL": "@database-url"
  }
}
```

## Cloudflare Workers

```javascript
// wrangler.toml
// name = "my-worker"
// main = "src/index.js"
// compatibility_date = "2024-01-01"

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === '/api/hello') {
      return new Response(
        JSON.stringify({ message: 'Hello from Workers!' }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }

    return env.ASSETS.fetch(request);
  },
};
```

## Docker to Cloud

```dockerfile
# Multi-stage for production
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
WORKDIR /app
COPY --from=builder --chown=nextjs:nodejs /app/dist ./dist
COPY --from=builder --chown=nextjs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nodejs /app/package.json ./package.json
USER nextjs
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Secrets stored in cloud secret manager
- [ ] Health check endpoint implemented
- [ ] Graceful shutdown handler
- [ ] Logging configured (stdout/stderr)
- [ ] Metrics endpoint (Prometheus/CloudWatch)
- [ ] CDN configured for static assets
- [ ] TLS/SSL certificates
- [ ] DNS configured
- [ ] Auto-scaling policies set
- [ ] Rollback strategy defined
