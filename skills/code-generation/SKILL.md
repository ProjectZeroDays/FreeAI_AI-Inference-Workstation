---
name: code-generation
description: Code scaffolding, boilerplate generation, project templates, and automated code creation. Use when the user asks about generating boilerplate code, scaffolding projects, creating templates, or automated code generation for new components, APIs, or modules.
---

# Code Generation

## Project Scaffolding

### Node.js API (Express + TypeScript)

```bash
# Directory structure
myapi/
├── src/
│   ├── routes/
│   │   └── index.ts
│   ├── middleware/
│   │   └── error.ts
│   ├── services/
│   ├── models/
│   └── index.ts
├── tests/
├── package.json
├── tsconfig.json
└── .env.example
```

```json
// package.json template
{
  "name": "{{name}}",
  "version": "1.0.0",
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest",
    "lint": "eslint src/"
  },
  "dependencies": {
    "express": "^4.18.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "tsx": "^4.0.0",
    "typescript": "^5.3.0",
    "vitest": "^1.0.0"
  }
}
```

### React Component Generator

```typescript
// Template: React functional component
interface {{Name}}Props {
  // Define props here
}

export function {{Name}}({}: {{Name}}Props) {
  return (
    <div>
      {/* Component content */}
    </div>
  );
}
```

### Python Module Generator

```python
# Template: Python module
"""{{module_name}} - Brief description"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class {{ClassName}}:
    """{{ClassName}} description."""
    
    id: str
    name: str
    created_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "{{ClassName}}":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=data.get("created_at"),
        )
```

## CRUD Generator

```typescript
// Input: Entity definition
interface Entity {
  name: string;
  fields: { name: string; type: string; required: boolean }[];
}

// Output: Generated files
function generateCRUD(entity: Entity) {
  return {
    model: generateModel(entity),
    repository: generateRepository(entity),
    service: generateService(entity),
    routes: generateRoutes(entity),
    tests: generateTests(entity),
  };
}

function generateModel(entity: Entity): string {
  const fields = entity.fields
    .map(f => `  ${f.name}: ${f.type}${f.required ? '' : ' | undefined'};`)
    .join('\n');
  
  return `export interface ${entity.name} {\n${fields}\n}`;
}

function generateRepository(entity: Entity): string {
  return `
export class ${entity.name}Repository {
  async findAll(): Promise<${entity.name}[]> {
    // TODO: Implement
    return [];
  }

  async findById(id: string): Promise<${entity.name} | null> {
    // TODO: Implement
    return null;
  }

  async create(data: Omit<${entity.name}, 'id'>): Promise<${entity.name}> {
    // TODO: Implement
    throw new Error('Not implemented');
  }

  async update(id: string, data: Partial<${entity.name}>): Promise<${entity.name}> {
    // TODO: Implement
    throw new Error('Not implemented');
  }

  async delete(id: string): Promise<void> {
    // TODO: Implement
  }
}`;
}
```

## API Route Generator

```typescript
function generateRoutes(entity: Entity): string {
  const name = entity.name.toLowerCase();
  
  return `
import { Router } from 'express';
import { ${entity.name}Service } from '../services/${name}';

const router = Router();
const service = new ${entity.name}Service();

router.get('/${name}s', async (req, res) => {
  const items = await service.findAll();
  res.json({ data: items });
});

router.get('/${name}s/:id', async (req, res) => {
  const item = await service.findById(req.params.id);
  if (!item) return res.status(404).json({ error: 'Not found' });
  res.json({ data: item });
});

router.post('/${name}s', async (req, res) => {
  const item = await service.create(req.body);
  res.status(201).json({ data: item });
});

router.put('/${name}s/:id', async (req, res) => {
  const item = await service.update(req.params.id, req.body);
  res.json({ data: item });
});

router.delete('/${name}s/:id', async (req, res) => {
  await service.delete(req.params.id);
  res.status(204).end();
});

export default router;`;
}
```

## Database Migration Generator

```python
def generate_migration(name: str, fields: list[dict]) -> str:
    """Generate SQL migration from field definitions."""
    columns = []
    for field in fields:
        col = f"    {field['name']} {field['type']}"
        if field.get('primary'):
            col += " PRIMARY KEY"
        if field.get('not_null'):
            col += " NOT NULL"
        if field.get('default'):
            col += f" DEFAULT {field['default']}"
        columns.append(col)
    
    return f"""-- Migration: {name}
CREATE TABLE IF NOT EXISTS {name} (
{chr(10).join(columns)}
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_{name}_id ON {name}(id);
"""
```

## Test Generator

```typescript
function generateTests(entity: Entity): string {
  const name = entity.name.toLowerCase();
  
  return `
import { describe, it, expect, beforeEach } from 'vitest';
import { ${entity.name}Service } from '../services/${name}';

describe('${entity.name}Service', () => {
  let service: ${entity.name}Service;

  beforeEach(() => {
    service = new ${entity.name}Service();
  });

  describe('findAll', () => {
    it('should return empty array initially', async () => {
      const result = await service.findAll();
      expect(result).toEqual([]);
    });
  });

  describe('create', () => {
    it('should create a new ${name}', async () => {
      const data = { /* test data */ };
      const result = await service.create(data);
      expect(result).toHaveProperty('id');
    });
  });

  describe('findById', () => {
    it('should return null for non-existent id', async () => {
      const result = await service.findById('non-existent');
      expect(result).toBeNull();
    });
  });
});`;
}
```

## Configuration Generator

```typescript
// .env.example generator
function generateEnvExample(config: Record<string, { type: string; description: string }>): string {
  return Object.entries(config)
    .map(([key, { description }]) => `# ${description}\n${key}=`)
    .join('\n\n');
}

// Docker Compose generator
function generateDockerCompose(services: Service[]): string {
  const compose = {
    version: '3.8',
    services: services.reduce((acc, svc) => ({
      ...acc,
      [svc.name]: {
        build: svc.dockerfile ? '.' : undefined,
        image: svc.image,
        ports: svc.ports?.map(p => `${p}:${p}`),
        environment: svc.env,
        depends_on: svc.dependsOn,
      },
    }), {}),
  };
  return JSON.stringify(compose, null, 2);
}
```

## Best Practices

1. Generate only what's needed
2. Keep generated code simple and readable
3. Allow customization via templates
4. Include TODO markers for manual implementation
5. Test generated code
6. Version templates alongside generated code
7. Don't over-generate — simple is better
