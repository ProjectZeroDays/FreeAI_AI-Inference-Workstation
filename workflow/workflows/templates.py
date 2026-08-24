"""Ready-made workflow templates."""
try:
    from workflow.engine import Step, Workflow
except ImportError:
    from engine import Step, Workflow


# --------------------------- API build ---------------------------

def api_arch_prompt(ctx):
    return {
        "context": ctx["spec"],
        "question": "Design the REST API: endpoints, request/response "
                    "schemas, error model, and auth strategy.",
        "max_tokens": 4096,
    }


def api_codegen_prompt(ctx):
    arch = str(ctx.get("architecture", {}).get("response", ""))
    return {
        "prompt": f"Implement production code for this API design:\n{arch}",
        "max_tokens": 4096,
    }


api_arch_step = Step("architecture", "analyze", api_arch_prompt)
api_codegen_step = Step("codegen", "orchestrate", api_codegen_prompt,
                        consumes=["architecture"])

API_BUILD_WORKFLOW = Workflow(
    name="api_build",
    steps=[api_arch_step, api_codegen_step],
)


# ----------------------- Microservice build -----------------------

def ms_design_prompt(ctx):
    return {
        "context": ctx["spec"],
        "question": "Decompose into microservices: service boundaries, "
                    "ownership, data stores, and inter-service contracts.",
        "max_tokens": 4096,
    }


def ms_scaffold_prompt(ctx):
    design = str(ctx.get("design", {}).get("response", ""))
    return {
        "prompt": f"Scaffold each microservice described here:\n{design}\n"
                  f"Include Dockerfiles and CI outlines.",
        "max_tokens": 4096,
    }


def ms_review_prompt(ctx):
    scaffold = str(ctx.get("scaffold", {}).get("response", ""))
    return {
        "context": scaffold,
        "question": "Review for production readiness: failure modes, "
                    "observability gaps, and scaling risks.",
        "max_tokens": 2048,
    }


ms_design_step = Step("design", "analyze", ms_design_prompt)
ms_scaffold_step = Step("scaffold", "orchestrate", ms_scaffold_prompt,
                        consumes=["design"])
ms_review_step = Step("review", "analyze", ms_review_prompt,
                      consumes=["scaffold"])

MICROSERVICE_BUILD_WORKFLOW = Workflow(
    name="microservice_build",
    steps=[ms_design_step, ms_scaffold_step, ms_review_step],
)
