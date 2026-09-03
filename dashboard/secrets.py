"""Re-export secrets module for backward compatibility."""
from dashboard.secrets_helpers import *  # noqa: F401, F403
from dashboard.secrets_helpers import (  # noqa: F401
    SECRETS_DIR,
    METADATA_PATH,
    _IN_MEMORY,
    _get_master_key,
    store_secret,
    get_secret,
    delete_secret,
    list_secrets,
    rotate_secret,
    import_secrets,
    export_secrets,
    get_secret_metadata,
)
