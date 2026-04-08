import os


class AtlasSettings:
    """Atlas configuration with environment variable support"""

    ATLAS_URL: str = os.getenv("ATLAS_URL", "http://localhost:23000")
    USERNAME: str = os.getenv("ATLAS_USERNAME", "admin")
    PASSWORD: str = os.getenv("ATLAS_PASSWORD", "admin")

    @classmethod
    def from_env(cls) -> "AtlasSettings":
        """
        Creates AtlasSettings instance from environment variables.

        Returns:
            AtlasSettings: Configuration loaded from environment variables.
        """
        return cls()

    @classmethod
    def from_config(cls, atlas_url: str, username: str, password: str) -> "AtlasSettings":
        """
        Creates AtlasSettings instance from explicit configuration.

        Args:
            atlas_url: The URL of the Atlas server.
            username: The username for authentication.
            password: The password for authentication.

        Returns:
            AtlasSettings: Configuration instance.
        """
        settings = cls()
        settings.ATLAS_URL = atlas_url
        settings.USERNAME = username
        settings.PASSWORD = password
        return settings


# Default singleton instance
settings = AtlasSettings() 