from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, computed_field, Field

from ..atlas_type_def import prepare_qualified_name


class LifecycleStatusEnum(str, Enum):
    """Enum for lifecycle status."""

    IDEATE_PROPOSE = "Ideate & Propose"
    DEFINE_DESIGN = "Define & Design"
    DEVELOP_BUILD = "Develop & Build"
    VALIDATE_APPROVE = "Validate & Approve"
    PUBLISH_CONSUME = "Publish & Consume"
    MONITOR_MAINTAIN = "Monitor & Maintain"
    CHANGE_RETIRE = "Change & Retire"

class SensitivityEnum(str, Enum):
    """Enum for Sensitity indicator"""

    SENSITITY_INTERNAL = "SCB Sensitive Internal"
    SENSITIVITY_EXTERNAL = "SCB Sensitive External"

class RefreshCutEnum(str, Enum):
    """Enum for Refresh Cut"""

    ACTUAL_CUT = "Actual"

class RefreshFrequencyEnum(str, Enum):
    """Enum for Refresh Frequency"""

    DAILY = "Daily (T+0)"

class GranularityEnum(str, Enum):
    """Enum for Data Product Granularity"""

    TRADE = "Trade"
    TRADE_LEGS = "Trade + Legs"
    INCREMENTAL = "Incremental"
    PORTFOLIO = "Portfolio"
    CONTRACT = "Contract"
    TRANSACTION = "Transaction"
    ACCOUNT = "Account"

class DataProductBasicMetadata(BaseModel):
    """Basic metadata for Data Product."""

    data_product_name: str
    description: str = ""
    data_product_category: str = "Source-Aligned"
    granularity: Optional[GranularityEnum] | None = None
    tags: Optional[List[str]] = None

    def __init__(
        self,
        *,
        data_product_name: str,
        description: str = "",
        data_product_category: str = "Source-Aligned",
        granularity: Optional[GranularityEnum] | None = None,
        tags: Optional[List[str]] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            data_product_name=data_product_name,
            description=description,
            data_product_category=data_product_category,
            granularity=granularity,
            tags=tags,
            **data,
        )


class DataProductBusinessMetadata(BaseModel):
    """Business metadata for Data Product."""

    business_purpose: str = ""
    gcfo_owner_name: Optional[str] = None
    gcfo_owner_contact: Optional[str] = None
    linked_entities: Optional[List[str]] = None


class DataProductClassification(BaseModel):
    """Classification metadata for Data Product."""

    sensitivity: SensitivityEnum = SensitivityEnum.SENSITITY_INTERNAL
    personal: bool = False
    geo_location_access: Optional[List[str]] = None
    regulatory_flags: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    approval: Optional[str] = None


class DataProductPorts(BaseModel):
    """Port information for Data Product (input/output)."""

    data_product_input_ports: Optional[List[str]] = None
    data_product_output_port: Optional[str] = None
    data_product_input_process: Optional[str] = None
    data_product_output_process: Optional[str] = None
    delivery_channels: Optional[List[str]] = None
    access_rules: Optional[str] = None
    data_landing_pattern: Optional[str] = None
    data_handshake: Optional[str] = None

    def __init__(
        self,
        *,
        data_product_input_ports: Optional[List[str]] = None,
        data_product_output_port: Optional[str] = None,
        data_product_input_process: Optional[str] = None,
        data_product_output_process: Optional[str] = None,
        delivery_channels: Optional[List[str]] = None,
        access_rules: Optional[str] = None,
        data_landing_pattern: Optional[str] = None,
        data_handshake: Optional[str] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            data_product_input_ports=data_product_input_ports,
            data_product_output_port=data_product_output_port,
            data_product_input_process=data_product_input_process,
            data_product_output_process=data_product_output_process,
            delivery_channels=delivery_channels,
            access_rules=access_rules,
            data_landing_pattern=data_landing_pattern,
            data_handshake=data_handshake,
            **data,
        )


class DataProductSchemaField(BaseModel):
    """Schema field metadata for a Data Product output port."""

    field_name: str
    field_type: Optional[str] = None
    field_description: Optional[str] = None
    category: Optional[str] = None
    is_cde: Optional[bool] = None

    def __init__(
        self,
        *,
        field_name: str,
        field_type: Optional[str] = None,
        field_description: Optional[str] = None,
        category: Optional[str] = None,
        is_cde: Optional[bool] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            field_name=field_name,
            field_type=field_type,
            field_description=field_description,
            category=category,
            is_cde=is_cde,
            **data,
        )

class DataProductMasterSchema(BaseModel):
    """Master schema for a Data Product output port."""

    data_product_name: str | None = None
    id: str | None = None
    category: str | None = None
    attribute_name: str | None = None
    source_of_attribute: str | None = None
    field_name: str | None = None
    data_type: str | None = None
    direct_derived: str | None = None
    description: str | None = None
    field_type: str | None = None
    current_source_attribute: str | None = None
    subledger_ds: str | None = None
    fdp_attribute_name: str | None = None
    derivation_logic: str | None = None
    is_cde: bool = False
    product_zone: str | None = None
    sample_value_1: str | None = None
    sample_value_2: str | None = None

    def __init__(
        self,
        *,
        data_product_name: str | None = None,
        id: str | None = None,
        category: str | None = None,
        attribute_name: str | None = None,
        source_of_attribute: str | None = None,
        field_name: str | None = None,
        field_type: str | None = None,
        direct_derived: str | None = None,
        description: str | None = None,
        data_type: str | None = None,
        current_source_attribute: str | None = None,
        subledger_ds: str | None = None,
        fdp_attribute_name: str | None = None,
        derivation_logic: str | None = None,
        is_cde: bool = False,
        product_zone: str | None = None,
        sample_value_1: str | None = None,
        sample_value_2: str | None = None,
        **data: Any
    ) -> None:
        super().__init__(
            data_product_name=data_product_name,
            id=id,
            category=category,
            attribute_name=attribute_name,
            source_of_attribute=source_of_attribute,
            field_name=field_name,
            field_type=field_type,
            direct_derived=direct_derived,
            description=description,
            data_type=data_type,
            current_source_attribute=current_source_attribute,
            subledger_ds=subledger_ds,
            fdp_attribute_name=fdp_attribute_name,
            derivation_logic=derivation_logic,
            is_cde=is_cde,
            product_zone=product_zone,
            sample_value_1=sample_value_1,
            sample_value_2=sample_value_2,
            **data
        )

class DataProductUsage(BaseModel):
    """Usage/Adoption metadata for Data Product."""

    users: Optional[List[str]] = Field(None, description="Current known users or group of users of the Data Product")
    systems: Optional[int] = Field(None, description="Number of consuming systems")
    usecases: Optional[List[str]] = Field(None, description="List of use cases")


class DataProductLifecycle(BaseModel):
    """Lifecycle metadata for Data Product."""

    version: Optional[str] = Field(None, description="Version of the data product")
    environment: Optional[str] = Field(None, description="Environment: Production, Staging, Dev")
    lifecycle_status: Optional[LifecycleStatusEnum] = Field(None, description="Lifecycle status")
    delivery_date: Optional[datetime] = Field(None, description="Delivery date")


class DataProductGovernanceMetadata(BaseModel):
    """Governance metadata for Data Product."""

    domain: str
    sub_domain: str = ""
    refresh_frequency: Optional[RefreshFrequencyEnum] = Field(None, description="Data refresh frequency")
    refresh_cut: Optional[RefreshCutEnum] = Field(None, description="Data refresh cut of the Data Product")
    last_refreshed: Optional[datetime] = Field(None, description="Last refreshed timestamp")
    data_product_owner: Optional[str] = None
    data_product_owner_contact_information: Optional[str] = None
    domain_owner: Optional[str] = None
    domain_owner_contact_information: Optional[str] = None
    data_steward: Optional[str] = None
    data_steward_contact_information: Optional[str] = None
    support_contact: Optional[str] = None
    support_contact_information: Optional[str] = None
    data_retention: Optional[str] = None
    sla: Optional[List[str]] = None
    communication_channel: Optional[List[str]] = None
    data_quality_score: Optional[str] = Field(None, description="Data quality score/indicator")
    resolution_sla: Optional[str] = Field(None, description="Resolution SLA for data product issues")
    completeness: Optional[str] = Field(None, description="Data completeness indicator")
    
    def __init__(
        self,
        *,
        domain: str,
        sub_domain: str = "",
        refresh_frequency: Optional[RefreshFrequencyEnum] = None,
        data_product_owner: Optional[str] = None,
        data_product_owner_contact_information: Optional[str] = None,
        domain_owner: Optional[str] = None,
        domain_owner_contact_information: Optional[str] = None,
        data_steward: Optional[str] = None,
        data_steward_contact_information: Optional[str] = None,
        support_contact: Optional[str] = None,
        support_contact_information: Optional[str] = None,
        data_retention: Optional[str] = None,
        sla: Optional[str] = None,
        communication_channel: Optional[List[str]] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            domain=domain,
            sub_domain=sub_domain,
            refresh_frequency=refresh_frequency,
            data_product_owner=data_product_owner,
            data_product_owner_contact_information=data_product_owner_contact_information,
            domain_owner=domain_owner,
            domain_owner_contact_information=domain_owner_contact_information,
            data_steward=data_steward,
            data_steward_contact_information=data_steward_contact_information,
            support_contact=support_contact,
            support_contact_information=support_contact_information,
            data_retention=data_retention,
            sla=sla,
            communication_channel=communication_channel,
            **data,
        )


class CompleteDataProductModel(BaseModel):
    """Complete Data Product model combining all metadata."""

    basic_metadata: DataProductBasicMetadata
    business_metadata: Optional[DataProductBusinessMetadata] = None
    classification: Optional[DataProductClassification] = None
    ports: Optional[DataProductPorts] = None
    usage: Optional[DataProductUsage] = None
    lifecycle: Optional[DataProductLifecycle] = None
    governance_metadata: DataProductGovernanceMetadata
    output_port_schema: Optional[List[DataProductMasterSchema]] = None

    def __init__(
        self,
        *,
        basic_metadata: DataProductBasicMetadata,
        governance_metadata: DataProductGovernanceMetadata,
        business_metadata: Optional[DataProductBusinessMetadata] = None,
        classification: Optional[DataProductClassification] = None,
        ports: Optional[DataProductPorts] = None,
        usage: Optional[DataProductUsage] = None,
        lifecycle: Optional[DataProductLifecycle] = None,
        #output_port_schema: Optional[List[DataProductSchemaField]] = None,
        output_port_schema: Optional[List[DataProductMasterSchema]] = None,
        **data: Any,
    ) -> None:
        super().__init__(
            basic_metadata=basic_metadata,
            governance_metadata=governance_metadata,
            business_metadata=business_metadata,
            classification=classification,
            ports=ports,
            usage=usage,
            lifecycle=lifecycle,
            output_port_schema=output_port_schema,
            **data,
        )

    @computed_field
    @property
    def qualified_name(self) -> str:
        """Generate qualified name for the data product."""
        return prepare_qualified_name(self.basic_metadata.data_product_name)

    def to_atlas_entity(self) -> dict:
        """Convert to Atlas entity dictionary for SCB_DataProduct."""
        attrs: dict[str, Any] = {
            "owner": self.governance_metadata.domain_owner,
            "data_product_name": self.basic_metadata.data_product_name,
            "description": self.basic_metadata.description,
            "data_product_category": self.basic_metadata.data_product_category,
            "qualifiedName": self.qualified_name,
            "name": self.basic_metadata.data_product_name,
            "granularity": self.basic_metadata.granularity.value if self.basic_metadata.granularity else None,
        }

        if self.business_metadata:
            attrs["business_metadata"] = {
                "typeName": "SCB_BusinessInfo",
                "attributes": {
                    "business_purpose": self.business_metadata.business_purpose,
                    "gcfo_owner_name": self.business_metadata.gcfo_owner_name,
                    "gcfo_owner_contact": self.business_metadata.gcfo_owner_contact,
                    "linked_entities": self.business_metadata.linked_entities,
                },
            }

        if self.classification:
            attrs["flags"] = {
                "typeName": "SCB_Flags",
                "attributes": {
                    "geo_location_access": self.classification.geo_location_access or [],
                    "regulatory_flags": self.classification.regulatory_flags or [],
                    "certifications": self.classification.certifications or [],
                    "approvals": [self.classification.approval] if self.classification.approval else [],
                },
            }

        if self.ports:
            port_attributes = {
                "data_landing_pattern": self.ports.data_landing_pattern,
                "data_handshake": self.ports.data_handshake,
                "delivery_channel": self.ports.delivery_channels[0] if self.ports.delivery_channels else None,
                "access_rules": [self.ports.access_rules] if self.ports.access_rules else None,
            }
            attrs["data_access"] = [
                {
                    "typeName": "SCB_DataAccess",
                    "attributes": {k: v for k, v in port_attributes.items() if v is not None},
                }
            ]

        if self.usage:
            attrs["uses"] = {
                "typeName": "SCB_Adoption",
                "attributes": {
                    "users": [str(self.usage.users)] if self.usage.users is not None else [],
                    "num_systems": str(self.usage.systems) if self.usage.systems else "0",
                    "use_cases": self.usage.usecases or [],
                },
            }

        if self.lifecycle:
            attrs["lifecycle"] = {
                "typeName": "SCB_Lifecycle",
                "attributes": {
                    "lifecycle_status": self.lifecycle.lifecycle_status.value if self.lifecycle.lifecycle_status else None,
                    "environment": self.lifecycle.environment,
                    "delivery_date": self.lifecycle.delivery_date.isoformat() if self.lifecycle.delivery_date else None,
                },
            }

        if self.usage:
            attrs["uses"] = {
                "typeName": "SCB_Adoption",
                "attributes": {
                    "users": self.usage.users or [],
                    "num_systems": str(self.usage.systems) if self.usage.systems else "0",
                    "use_cases": self.usage.usecases or [],
                },
            }

        attrs["support_team"] = {
            "typeName": "SCB_SupportTeam",
            "attributes": {
                "source_domain_owner": self.governance_metadata.domain_owner,
                "source_domain_contact": self.governance_metadata.domain_owner_contact_information,
                "data_steward": self.governance_metadata.data_steward,
                "data_steward_contact": self.governance_metadata.data_steward_contact_information,
                "support_contact": [self.governance_metadata.support_contact] if self.governance_metadata.support_contact else [],
            },
        }

        attrs["sla"] = {
            "typeName": "SCB_Sla",
            "attributes": {
                "data_retention": self.governance_metadata.data_retention,
                "agreed_sla": self.governance_metadata.sla if self.governance_metadata.sla else [],
                "communication_channels": self.governance_metadata.communication_channel or [],
                "data_quality_score": self.governance_metadata.data_quality_score,
                "resolution_sla": self.governance_metadata.resolution_sla,
                "completeness": self.governance_metadata.completeness,
            },
        }

        attrs["freshness"] = {
            "typeName": "SCB_Freshness",
            "attributes": {
                "refresh_frequency": self.governance_metadata.refresh_frequency.value if self.governance_metadata.refresh_frequency else None,
                "refresh_cut": self.governance_metadata.refresh_cut.value if self.governance_metadata.refresh_cut else None,
                "last_refreshed": self.governance_metadata.last_refreshed.timestamp() if self.governance_metadata.last_refreshed else None
            },
        }

        attrs["business_domain"] = {
            "typeName": "SCB_BusinessDomain",
            "attributes": {
                "domain": self.governance_metadata.domain,
                "sub_domain": self.governance_metadata.sub_domain,
            },
        }

        # Add classification of the data product as label if sensitivity is defined.
        classifications_payload: list[dict[str, str]] = []
        if self.classification and self.classification.sensitivity:
            classifications_payload.append({"typeName": self.classification.sensitivity.value})
            
        return {
            "typeName": "SCB_DataProduct",
            "attributes": attrs,
            "classifications": classifications_payload,
        }

