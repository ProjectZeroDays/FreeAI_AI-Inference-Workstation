try:
    from workflow.engine import Step, Workflow
except ImportError:
    from engine import Step, Workflow


def arch_prompt(ctx):
    return {
        "context": ctx["spec"],
        "question": "Generate architecture, modules, and data models.",
        "max_tokens": 4096
    }


def codegen_prompt(ctx):
    arch = ctx.get("architecture", {}).get("response", "")
    return {
        "prompt": f"Generate production code for this architecture:\n{arch}",
        "max_tokens": 4096
    }


def testgen_prompt(ctx):
    code = ctx.get("codegen", {}).get("response", "")
    return {
        "prompt": f"Generate full test suite for this code:\n{code}",
        "max_tokens": 2048
    }


architecture_step = Step("architecture", "analyze", arch_prompt)
codegen_step = Step("codegen", "orchestrate", codegen_prompt,
                    consumes=["architecture"])
testgen_step = Step("tests", "orchestrate", testgen_prompt,
                    consumes=["codegen"])

FULL_BUILD_WORKFLOW = Workflow(
    name="full_build",
    steps=[architecture_step, codegen_step, testgen_step]
)
