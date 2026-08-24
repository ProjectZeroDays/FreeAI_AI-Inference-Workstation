#!/usr/bin/env python3
"""Auto-generate docs/workflows.json from the workflow registry."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.engine import Workflow, Step
from workflow.registry import WORKFLOWS


def describe_step(step: Step):
    return {
        "name": step.name,
        "agent": step.agent,
        "consumes": step.consumes,
        "produces": step.produces,
    }


def describe_workflow(name: str, wf: Workflow):
    return {
        "name": name,
        "steps": [describe_step(s) for s in wf.steps],
    }


def main():
    docs = {
        "workflows": [describe_workflow(name, wf)
                      for name, wf in WORKFLOWS.items()],
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "workflows.json")
    with open(out, "w") as f:
        json.dump(docs, f, indent=2)
    print("Generated", out)


if __name__ == "__main__":
    main()
