from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, computed_field

from ..atlas_type_def import prepare_qualified_name

def _now_epoch_millis() -> int:
    """Return current timestamp in milliseconds for Atlas `date` fields."""
    return int(datetime.now().timestamp() * 1000)

class DatabaseModel(BaseModel):
    """Pydantic model for SCB_Database entity."""

    database_name: str
    location_uri: str
    create_time: Optional[datetime] = None
    description: Optional[str] = ""

    def __init__(
        self,
        *,
        database_name: Optional[str] = None,
        location_uri: Optional[str] = None,
        create_time: Optional[datetime] = None,
        description: Optional[str] = "",
        **data: Any,
    ) -> None:
        super().__init__(
            database_name=database_name,
            location_uri=location_uri,
            create_time=create_time,
            description=description,
            **data,
        )

    @computed_field
    @property
    def qualified_name(self) -> str:
        """Generate qualified name for the database."""
        return prepare_qualified_name(self.database_name)

    def to_atlas_entity(self) -> dict:
        """Convert to Atlas entity dictionary."""
        return {
            "typeName": "SCB_Database",
            "attributes": {
                "database_name": self.database_name,
                "locationUri": self.location_uri,
                "createTime": self.create_time.timestamp() if self.create_time else None,
                "description": self.description,
                "qualifiedName": self.qualified_name,
                "name": self.database_name,
            },
        }

