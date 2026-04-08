from datetime import date, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, computed_field

from ..atlas_type_def import prepare_qualified_name


class PIIEnum(str, Enum):
    """Enum for PII indicator."""

    YES = "True"
    NO = "False"

class CDEEnum(str, Enum):

    Y = "True"
    N = "False"


class StandardColumnModel(BaseModel):
    """Pydantic model for standard column attributes."""

    field_name: str
    data_type: str
    table_name: Optional[str] = None
    database_name: Optional[str] = None
    category: Optional[str] = None
    attribute_name: Optional[str] = None
    source_of_attribute: Optional[str] = None
    direct_derived: Optional[str] = None
    description: Optional[str] = ""
    field_type: Optional[str] = None
    current_source_attribute: Optional[str] = None
    subledger_ds: Optional[str] = None
    fdp_attribute: Optional[str] = None
    derivation_logic: Optional[str] = None
    is_cde: Optional[CDEEnum] = CDEEnum.N
    product_zone: Optional[str] = None
    pii: Optional[PIIEnum] = PIIEnum.NO
    sample_value_1: Optional[str] = None
    sample_value_2: Optional[str] = None
    create_time: Optional[datetime] = None
    mdm_link: Optional[str] = None
    
    def __init__(
        self,
        *,
        field_name: str,
        data_type: str,
        table_name: Optional[str] = None,
        database_name: Optional[str] = None,
        category: Optional[str] = None,
        attribute_name: Optional[str] = None,
        source_of_attribute: Optional[str] = None,
        direct_derived: Optional[str] = None,
        description: Optional[str] = "",
        field_type: Optional[str] = None,
        current_source_attribute: Optional[str] = None,
        subledger_ds: Optional[str] = None,
        fdp_attribute: Optional[str] = None,
        derivation_logic: Optional[str] = None,
        is_cde: Optional[CDEEnum] = CDEEnum.N,
        product_zone: Optional[str] = None,
        pii: Optional[PIIEnum] = PIIEnum.NO,
        sample_value_1: Optional[str] = None,
        sample_value_2: Optional[str] = None,
        create_time: Optional[date] = None,
        mdm_link: Optional[str] = "https://example-mdm-link.sc.com",
        **data: Any,
    ) -> None:
        super().__init__(
            field_name=field_name,
            data_type=data_type,
            table_name=table_name,
            database_name=database_name,
            category=category,
            attribute_name=attribute_name,
            source_of_attribute=source_of_attribute,
            direct_derived=direct_derived,
            description=description,
            field_type=field_type,
            current_source_attribute=current_source_attribute,
            subledger_ds=subledger_ds,
            fdp_attribute=fdp_attribute,
            derivation_logic=derivation_logic,
            is_cde=is_cde,
            product_zone=product_zone,
            pii=pii,
            sample_value_1=sample_value_1,
            sample_value_2=sample_value_2,
            create_time=create_time,
            mdm_link=mdm_link,
            **data
        )
    
    @computed_field
    @property
    def qualified_name(self) -> str:
        """Generate qualified name for the column."""
        if self.database_name and self.table_name:
            return prepare_qualified_name(f"{self.database_name}.{self.table_name}.{self.field_name}")
        if self.table_name:
            return prepare_qualified_name(f"{self.table_name}.{self.field_name}")
        return prepare_qualified_name(self.field_name)

    def to_atlas_entity(self) -> dict:
        """Convert to Atlas entity dictionary."""
        create_time_ms = int(self.create_time.timestamp() * 1000) if self.create_time else None
        is_cde_bool = (self.is_cde == CDEEnum.Y) if self.is_cde is not None else None
        pii_bool = (self.pii == PIIEnum.YES) if self.pii is not None else None

        return {
            "typeName": "SCB_Column",
            "attributes": {
                "name": self.field_name,
                "field_name": self.field_name,
                "data_type": self.data_type,
                "category": self.category,
                "attribute_name": self.attribute_name,
                "source_of_attribute": self.source_of_attribute,
                "direct_derived": self.direct_derived,
                "description": self.description,
                "field_type": self.field_type,
                "current_source_attribute": self.current_source_attribute,
                "subledger_ds": self.subledger_ds,
                "fdp_attribute": self.fdp_attribute,
                "derivation_logic": self.derivation_logic,
                "is_cde": is_cde_bool,
                "product_zone": self.product_zone,
                "pii": pii_bool,
                "createTime": create_time_ms,
                "sample_value_1": self.sample_value_1,
                "sample_value_2": self.sample_value_2,
                "qualifiedName": self.qualified_name,
                "mdm_link": self.mdm_link,
                # Legacy aliases for compatibility with older Atlas schemas/readers.
                "column_name": self.field_name,
                "dataType": self.data_type,
                "comment": self.description,
            }
        }

# class ColumnModel(BaseModel):
#     """Pydantic model for SCB_Column entity."""

#     column_name: str
#     data_type: str
#     description: Optional[str] = ""
#     position: Optional[int] = None
#     table_name: Optional[str] = None
#     database_name: Optional[str] = None
#     pii: Optional[PIIEnum] = None
#     create_time: Optional[date] = None

#     def __init__(
#         self,
#         *,
#         column_name: str,
#         data_type: str,
#         description: Optional[str] = "",
#         position: Optional[int] = None,
#         table_name: Optional[str] = None,
#         database_name: Optional[str] = None,
#         pii: Optional[PIIEnum] = None,
#         create_time: Optional[date] = None,
#         **data: Any,
#     ) -> None:
#         super().__init__(
#             column_name=column_name,
#             data_type=data_type,
#             description=description,
#             position=position,
#             table_name=table_name,
#             database_name=database_name,
#             pii=pii,
#             create_time=create_time,
#             **data,
#         )

#     @computed_field
#     @property
#     def qualified_name(self) -> str:
#         """Generate qualified name for the column."""
#         if self.database_name and self.table_name:
#             return prepare_qualified_name(f"{self.database_name}.{self.table_name}.{self.column_name}")
#         if self.table_name:
#             return prepare_qualified_name(f"{self.table_name}.{self.column_name}")
#         return prepare_qualified_name(self.column_name)

#     def to_atlas_entity(self) -> dict:
#         """Convert to Atlas entity dictionary."""
#         return {
#             "typeName": "SCB_Column",
#             "attributes": {
#                 "column_name": self.column_name,
#                 "dataType": self.data_type,
#                 "comment": self.description,
#                 "position": self.position,
#                 "pii": self.pii.value if self.pii else None,
#                 "createTime": self.create_time.isoformat() if self.create_time else None,
#                 "qualifiedName": self.qualified_name,
#                 "name": self.column_name,
#             },
#         }

