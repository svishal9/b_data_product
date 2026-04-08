import logging

from apache_atlas.client.base_client import AtlasClient

from .atlas_settings import settings
from .exceptions import AtlasConnectionError

logger = logging.getLogger(__name__)

def create_atlas_client(
        username: str = settings.USERNAME, 
        password: str = settings.PASSWORD
) -> AtlasClient:
    """
    Creates an Atlas client instance using the provided username and password.

    Args:
        username (str): The username for authenticating with the Atlas API. Defaults to
            the value from ATLAS_USERNAME environment variable or "admin".
        password (str): The password for authenticating with the Atlas API. Defaults to
            the value from ATLAS_PASSWORD environment variable or "admin".

    Returns:
        AtlasClient: An instance of the AtlasClient class configured with the provided credentials.

    Raises:
        AtlasConnectionError: If unable to connect to the Atlas instance.
        AtlasAuthenticationError: If authentication with the Atlas instance fails.
    """
    try:
        client = AtlasClient(settings.ATLAS_URL, (username, password))
        logger.info(f"Successfully created Atlas client for {settings.ATLAS_URL}")
        return client
    except Exception as e:
        logger.error(f"Failed to create Atlas client: {e}")
        raise AtlasConnectionError(f"Unable to connect to Atlas at {settings.ATLAS_URL}: {e}") from e

