from typing import Any, Optional

from pydantic import BaseModel, computed_field

from ..atlas_type_def import prepare_qualified_name


class ProcessModel(BaseModel):
    """Pydantic model for SCB_Process entity."""

    process_name: str
    query_id: str
    query_text: str
    user_name: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None

    def __init__(
        self,
        *,
        process_name: str,
        query_id: str,
        query_text: str,
        user_name: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            process_name=process_name,
            query_id=query_id,
            query_text=query_text,
            user_name=user_name,
            start_time=start_time,
            end_time=end_time,
            **data,
        )

    @computed_field
    @property
    def qualified_name(self) -> str:
        """Generate qualified name for the process."""
        return prepare_qualified_name(f"proc_{self.query_id}")

    def to_atlas_entity(self) -> dict:
        """Convert to Atlas entity dictionary."""
        return {
            "typeName": "SCB_Process",
            "attributes": {
                "process_name": self.process_name,
                "queryId": self.query_id,
                "queryText": self.query_text,
                "userName": self.user_name,
                "startTime": self.start_time,
                "endTime": self.end_time,
                "qualifiedName": self.qualified_name,
                "name": self.process_name,
            },
        }

