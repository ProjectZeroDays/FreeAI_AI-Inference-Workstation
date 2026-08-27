# FreeAI Workflow Validation module.
"""Validate workflow step definitions: required fields, consumes/produces,
circular dependencies, and referential integrity."""
from typing import Dict, List, Set, Tuple


def validate_workflow(
    steps: List,
    initial_keys: List[str] = None,
) -> List[str]:
    """Validate a workflow definition.

    Checks:
    - Every step has ``consumes`` and ``produces`` defined (non-null).
    - Required fields are present on each step (``name``).
    - No circular dependency chains among step names.
    - Every value in ``consumes`` is either an ``initial_keys`` entry or
      the ``name`` / ``produces`` of a preceding step.
    """
    warnings: List[str] = []
    step_names: Set[str] = set()
    produces_map: Dict[str, Set[str]] = {}
    consumes_map: Dict[str, Set[str]] = {}
    available: Set[str] = set(initial_keys or [])

    for idx, step in enumerate(steps):
        name = getattr(step, "name", None)

        # --- required field: name ---
        if not name:
            warnings.append(f"step at index {idx} is missing 'name'")
            name = f"<unnamed-{idx}>"

        step_names.add(name)

        # --- required fields: consumes / produces ---
        consumes = getattr(step, "consumes", None)
        produces = getattr(step, "produces", None)

        if consumes is None:
            warnings.append(
                f"step '{name}' is missing 'consumes' field"
            )
            consumes = []
        if produces is None:
            warnings.append(
                f"step '{name}' is missing 'produces' field"
            )
            produces = []

        consumes_set = set(consumes) if consumes else set()
        produces_set = set(produces) if produces else set()

        consumes_map[name] = consumes_set
        produces_map[name] = produces_set

        # --- dependency reference checks ---
        for dep in consumes_set:
            if dep not in available:
                warnings.append(
                    f"step '{name}' consumes '{dep}' "
                    f"but nothing provides it before it"
                )

        # build reachable set for cycle detection
        available.add(name)
        available.update(produces_set)

    # --- circular-dependency detection ---
    cycles = _detect_cycles(step_names, consumes_map)
    for cycle in cycles:
        warnings.append(
            f"circular dependency detected: {' -> '.join(cycle)}"
        )

    return warnings


def _detect_cycles(
    step_names: Set[str],
    consumes_map: Dict[str, Set[str]],
) -> List[List[str]]:
    """Return all elementary cycles in the step-dependency graph."""
    cycles: List[List[str]] = []
    visited: Set[str] = set()
    rec_stack: List[str] = []
    rec_set: Set[str] = set()

    def _dfs(node: str) -> None:
        visited.add(node)
        rec_stack.append(node)
        rec_set.add(node)

        for neighbour in consumes_map.get(node, set()):
            if neighbour not in step_names:
                continue
            if neighbour not in visited:
                _dfs(neighbour)
            elif neighbour in rec_set:
                idx = rec_stack.index(neighbour)
                cycle = rec_stack[idx:] + [neighbour]
                cycles.append(cycle)

        rec_stack.pop()
        rec_set.remove(node)

    for name in step_names:
        if name not in visited:
            _dfs(name)

    return cycles
