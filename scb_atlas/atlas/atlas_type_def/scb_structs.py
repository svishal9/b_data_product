from .base import BaseStructCategory

scb_adoption = BaseStructCategory(
    atlas_name="SCB_Adoption",
    attributes=[
        { "name": "users", "displayName": "User", "typeName": "array<string>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "num_systems", "displayName": "Number of Systems", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "use_cases", "displayName": "Use Cases", "typeName": "array<string>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_business_info = BaseStructCategory(
    atlas_name="SCB_BusinessInfo",
    attributes=[
        { "name": "gcfo_owner_name", "displayName": "GCFO Owner", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "gcfo_owner_contact", "displayName": "GCFO Owner Contact", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "business_purpose", "displayName": "Business Purpose",  "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False, "options": {"maxStrLength": 100} },
        { "name": "linked_entities", "displayName": "Linked Entities", "typeName": "array<string>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False, "options": {"maxStrLength": 100}  },
        { "name": "taxonomy", "displayName": "Taxonomy", "typeName": "array<SCB_Taxonomy>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_flags = BaseStructCategory(
    atlas_name="SCB_Flags",
    attributes=[
        { "name": "geo_location_access", "displayName": "Geo-Location Access", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "regulatory_flags", "displayName": "Regulatory Flags", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "certifications", "displayName": "Certifications", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "approvals", "displayName": "Approvals", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_data_access = BaseStructCategory(
    atlas_name="SCB_DataAccess",
    attributes=[
        { "name": "data_landing_pattern", "displayName": "Data Landing Pattern", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "data_handshake", "displayName": "Data Handshake", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "access_rules", "displayName": "Access Rules", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "delivery_channel", "displayName": "Delivery Channel", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_business_domain = BaseStructCategory(
    atlas_name="SCB_BusinessDomain",
    attributes=[
        { "name": "domain", "displayName": "Domain", "typeName": "SCB_Domain", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "sub_domain", "displayName": "Sub Domain", "typeName": "SCB_SubDomain", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_lifecycle = BaseStructCategory(
    atlas_name="SCB_Lifecycle",
    attributes=[
        { "name": "environment", "displayName": "Environment", "typeName": "SCB_Environment", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "delivery_date", "displayName": "Delivery Date", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_freshness = BaseStructCategory(
    atlas_name="SCB_Freshness",
    attributes=[
        { "name": "refresh_frequency", "displayName": "Refresh Frequency", "typeName": "SCB_RefreshFrequency",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "refresh_cut", "displayName": "Refresh Cut", "typeName": "SCB_RefreshCut",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "last_refreshed", "displayName": "Last Refreshed", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_support_team= BaseStructCategory(
    atlas_name="SCB_SupportTeam",
    attributes=[
        { "name": "source_domain_owner", "displayName": "Source Domain Owner", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "source_domain_contact", "displayName": "Source Domain Contact", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "data_steward", "displayName": "Data Steward", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "data_steward_contact", "displayName": "Data Steward Contact", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "support_contact", "displayName": "Support Contact", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_sla = BaseStructCategory(
    atlas_name="SCB_Sla",
    attributes=[
        { "name": "data_retention", "displayName": "Data Retention", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "agreed_sla", "displayName": "Agreed SLA", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "data_quality_score", "displayName": "Data Quality", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "resolution_sla", "displayName": "Resolution SLA", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "communication_channels", "displayName": "Communication Channels", "typeName": "array<string>",   "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "completeness", "displayName": "Data Completeness", "typeName": "string",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

scb_taxonomy = BaseStructCategory(
    atlas_name="SCB_Taxonomy",
    attributes=[
        { "name": "item", "displayName": "Item", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "meaning", "displayName": "Business Meaning", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
    ]
)

struct_names = [
    scb_adoption.atlas_name,
    scb_business_domain.atlas_name,
    scb_business_info.atlas_name,    
    scb_data_access.atlas_name,
    scb_flags.atlas_name,
    scb_freshness.atlas_name,
    scb_lifecycle.atlas_name,
    scb_support_team.atlas_name,
    scb_sla.atlas_name,
    scb_taxonomy.atlas_name
]

all_structs = [
    scb_taxonomy.prepare_atlas_type_definition(),
    scb_adoption.prepare_atlas_type_definition(),
    scb_business_domain.prepare_atlas_type_definition(),
    scb_business_info.prepare_atlas_type_definition(),
    scb_data_access.prepare_atlas_type_definition(),
    scb_flags.prepare_atlas_type_definition(),
    scb_freshness.prepare_atlas_type_definition(),
    scb_lifecycle.prepare_atlas_type_definition(),
    scb_support_team.prepare_atlas_type_definition(),
    scb_sla.prepare_atlas_type_definition(),
]