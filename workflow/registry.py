try:
    from workflow.engine import PROJECT_WORKFLOW
except ImportError:
    from engine import PROJECT_WORKFLOW

try:
    from workflow.workflows.full_build import FULL_BUILD_WORKFLOW
except ImportError:
    from workflows.full_build import FULL_BUILD_WORKFLOW

try:
    from workflow.workflows.templates import API_BUILD_WORKFLOW, \
        MICROSERVICE_BUILD_WORKFLOW
except ImportError:
    from workflows.templates import API_BUILD_WORKFLOW, \
        MICROSERVICE_BUILD_WORKFLOW

WORKFLOWS = {
    "project_pipeline": PROJECT_WORKFLOW,
    "full_build": FULL_BUILD_WORKFLOW,
    "api_build": API_BUILD_WORKFLOW,
    "microservice_build": MICROSERVICE_BUILD_WORKFLOW,
}


def get_workflow(name: str):
    return WORKFLOWS.get(name)


def list_workflows():
    return sorted(WORKFLOWS.keys())
