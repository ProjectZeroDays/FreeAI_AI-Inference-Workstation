---
name: quantum-module-writer
description: Creates new defensive modules for the Quantum framework following established conventions. Use when adding detection rules, hunting modules, threat intel feeds, ML models, or compliance checks.
---

# Quantum Module Writer

Creates new defensive modules following the Quantum framework conventions.

## Module Structure

All modules live in `core/` subdirectories:

```
core/
├── detection/          # Detection rules (YARA, SIGMA)
├── hunting/            # Threat hunting modules
├── threat_intel/       # Threat intelligence feeds
├── ml/                 # ML/AI models
├── compliance/         # Compliance checks (NIST, CMMC)
├── operational_planning/  # Operational planning modules
├── simulation/         # Simulation sandboxes
└── ...
```

## Module Template

```python
"""
Quantum Framework - [Module Name]
Defensive module for [purpose]
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class [ModuleName]:
    """[Brief description of what this module does]."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.initialized = False
        logger.info(f"[ModuleName] initialized")

    def initialize(self) -> bool:
        """Initialize the module. Return True on success."""
        try:
            # Setup logic here
            self.initialized = True
            logger.info("[ModuleName] initialized successfully")
            return True
        except Exception as e:
            logger.error(f"[ModuleName] init failed: {e}")
            return False

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the module's primary function."""
        if not self.initialized:
            return {"status": "error", "message": "Not initialized"}

        try:
            # Core logic here
            result = {
                "status": "success",
                "module": "ModuleName",
                "data": {},
                "timestamp": self._get_timestamp()
            }
            return result
        except Exception as e:
            logger.error(f"[ModuleName] execution failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Return current module status."""
        return {
            "module": "ModuleName",
            "initialized": self.initialized,
            "type": "defensive"
        }

    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
```

## Test Template

```python
"""
Tests for [Module Name]
"""
import pytest
from core.[path].[module_file] import [ModuleName]


class Test[ModuleName]:
    """Test suite for [ModuleName]."""

    def setup_method(self):
        self.module = [ModuleName]()

    def test_initialize(self):
        assert self.module.initialize() is True
        assert self.module.initialized is True

    def test_execute_before_init(self):
        result = self.module.execute()
        assert result["status"] == "error"

    def test_execute_after_init(self):
        self.module.initialize()
        result = self.module.execute()
        assert result["status"] == "success"

    def test_get_status(self):
        status = self.module.get_status()
        assert "module" in status
        assert status["type"] == "defensive"
```

## Rules

- **DEFENSIVE ONLY**: Only create modules for defensive purposes (detection, hunting, protection, compliance)
- **Never touch offensive components**: No exploit modules, no attack tools
- **All modules must have tests**: Follow TDD pattern from tdd-restoration skill
- **Log everything**: Use Python `logging` module, not print()
- **Type hints**: Use `typing` module for all function signatures
- **Error handling**: Return structured `{"status": "success/error", ...}` dicts
- **Config-driven**: Accept optional `config` dict for flexibility
