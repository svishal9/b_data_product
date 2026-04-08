from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, computed_field

from ..atlas_type_def import prepare_qualified_name


class TableTypeEnum(str, Enum):
    """Enum for table types."""

    MANAGED = "MANAGED"
    EXTERNAL = "EXTERNAL"


class TableModel(BaseModel):
    """Pydantic model for SCB_Table entity."""

    table_name: str
    database_name: Optional[str] = None
    description: Optional[str] = ""
    table_type: Optional[TableTypeEnum] = None
    create_time: Optional[datetime] = None
    temporary: Optional[bool] = False
    serde1: Optional[str] = None
    serde2: Optional[str] = None

    def __init__(
        self,
        *,
        table_name: str,
        database_name: Optional[str] = None,
        description: Optional[str] = "",
        table_type: Optional[TableTypeEnum] = None,
        create_time: Optional[datetime] = None,
        temporary: Optional[bool] = False,
        serde1: Optional[str] = None,
        serde2: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            table_name=table_name,
            database_name=database_name,
            description=description,
            table_type=table_type,
            create_time=create_time,
            temporary=temporary,
            serde1=serde1,
            serde2=serde2,
            **data,
        )

    @computed_field
    @property
    def qualified_name(self) -> str:
        """Generate qualified name for the table."""
        if self.database_name:
            return prepare_qualified_name(f"{self.database_name}.{self.table_name}")
        return prepare_qualified_name(self.table_name)

    def to_atlas_entity(self) -> dict:
        """Convert to Atlas entity dictionary."""
        return {
            "typeName": "SCB_Table",
            "attributes": {
                "table_name": self.table_name,
                "description": self.description,
                "tableType": self.table_type.value if self.table_type else None,
                "createTime": self.create_time.timestamp() if self.create_time else None,
                "temporary": self.temporary,
                "serde1": self.serde1,
                "serde2": self.serde2,
                "qualifiedName": self.qualified_name,
                "name": self.table_name,
            },
        }

