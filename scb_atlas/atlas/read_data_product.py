from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .service.entity_service import (
    create_column_from_model,
    create_data_product_from_model,
    create_database_from_model,
    create_process_from_model,
    create_table_from_model,
)
from .metadata_models import (
    StandardColumnModel,
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductBusinessMetadata,
    DataProductClassification,
    DataProductGovernanceMetadata,
    DataProductLifecycle,
    DataProductPorts,
    DataProductMasterSchema,
    DataProductUsage,
    DatabaseModel,
    ProcessModel,
    SensitivityEnum,
    GranularityEnum,
    TableModel,
)

_DATA_PRODUCT_SHEET_ALIASES = {"data product", "data_product", "data-product", "source data product"}
_STRICT_DATA_PRODUCT_REQUIRED_HEADERS = {
    "Data Product Name",
    "Description",
    "Domain",
    "Sub-Domain",
    "Data Product Category",
}
_DATA_SCHEMA_SHEET_ALIASES = {"schema", "data product schema", "data_product_schema", "data-product-schema", "master schema"}

_DATA_PRODUCT_CATEGORY_MAP = {
    "source aligned": "Source-Aligned",
    "source-aligned": "Source-Aligned",
    "consumer aligned": "Consumer-Aligned",
    "consumer-aligned": "Consumer-Aligned",
}
_REFRESH_FREQUENCY_MAP = {
    "daily(t+0)": "Daily (T+0)",
    "daily (t+0)": "Daily (T+0)",
    "Daily(T+0)": "Dailty (T+0)"
}
_REFRESH_CUT_MAP = {
    "Actual": "Actual",
    "actual": "Actual"
}

_SENSITIVITY_MAP = {
    "internal": "SCB Sensitive Internal",
    "external": "SCB Sensitive External",
    "scb sensitive internal": "SCB Sensitive Internal",
    "scb sensitive external": "SCB Sensitive External",
}
_GRANULARITY_MAP = {
    "trade": "Trade",
    "trade+legs": "Trade + Legs",
    "trade legs": "Trade + Legs",
    "incremental": "Incremental",
    "portfolio": "Portfolio",
    "contract": "Contract",
    "transaction": "Transaction",
    "account": "Account"
}

def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_header(value: Any) -> str:
    return _normalize_text(value).lower().replace("_", " ")


def _to_list(value: Any) -> list[str]:
    text = _normalize_text(value)
    if not text:
        return []
    normalized = text.replace("\n", ",").replace("/", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]

def _to_tag_list(values: Any) -> list[str]:
    tag_list = _to_list(values)
    tag_list = [tag.replace(" ", "-") for tag in tag_list]
    return tag_list


def _to_bool(value: Any) -> bool:
    text = _normalize_text(value).lower()
    return text in {"true", "yes", "y", "1"}


def _to_bool_or_raise(value: Any, *, field_name: str, strict: bool) -> bool:
    text = _normalize_text(value)
    if not text:
        return False
    normalized = text.lower()
    valid_true = {"true", "yes", "y", "1"}
    valid_false = {"false", "no", "n", "0"}
    if normalized in valid_true:
        return True
    if normalized in valid_false:
        return False
    if strict:
        raise ValueError(f"Invalid boolean value '{text}' for '{field_name}'.")
    return False


def _to_int_or_none(value: Any) -> int | None:
    text = _normalize_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _first_non_empty(row: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = row.get(key)
        if _normalize_text(value):
            return value
    return None


def _slugify_identifier(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in value)
    compact = "_".join(part for part in cleaned.split("_") if part)
    return compact or "data_product"


def _derive_output_port_table_name(model: CompleteDataProductModel) -> str:
    explicit = (model.ports.data_product_output_port if model.ports else None) or ""
    explicit_name = _normalize_text(explicit)
    if explicit_name:
        return _slugify_identifier(explicit_name)
    return f"{_slugify_identifier(model.basic_metadata.data_product_name)}_output_port"


def _derive_output_port_database_name(model: CompleteDataProductModel) -> str:
    domain = _slugify_identifier(model.governance_metadata.domain)
    return f"{domain}_data_products"


def _ensure_port_database(atlas_client: Any, model: CompleteDataProductModel) -> DatabaseModel:

    database_name = _derive_output_port_database_name(model)
    database_model = DatabaseModel(
        database_name=database_name,
        location_uri=f"atlas://scb/{database_name}",
        create_time=datetime.now(timezone.utc),
        description="",
    )
    create_database_from_model(atlas_client, database_model)
    return database_model


def _create_output_port_assets(
    atlas_client: Any,
    model: CompleteDataProductModel,
    database_model: DatabaseModel | None = None,
) -> str | None:
    database_model = database_model or _ensure_port_database(atlas_client, model)
    database_name = database_model.database_name

    table_name = _derive_output_port_table_name(model)
    table_model = TableModel(
        table_name=table_name,
        database_name=database_name,
        description=f"Output port for data product {model.basic_metadata.data_product_name}",
        table_type=None,
        create_time=None,
        temporary=False,
        serde1=None,
        serde2=None,
    )
    create_table_from_model(
        atlas_client,
        table_model,
        database_qualified_name=database_model.qualified_name,
    )

    for index, field in enumerate(model.output_port_schema or [], start=1):
        if not _normalize_text(field.field_name):
            continue
        column_model = StandardColumnModel(
            field_name=_slugify_identifier(field.field_name),
            data_type=_normalize_text(field.field_type) or "string",
            database_name=database_name,
            table_name=table_model.table_name,
            category=_normalize_text(field.category) or None,
            attribute_name=_normalize_text(field.attribute_name) or None,
            source_of_attribute=_normalize_text(field.source_of_attribute) or None,
            direct_derived=_normalize_text(field.direct_derived) or None,
            description=_normalize_text(field.description) or None,
            field_type=_normalize_text(field.field_type) or None,
            current_source_attribute=_normalize_text(field.current_source_attribute) or None,
            subledger_ds=_normalize_text(field.subledger_ds) or None,
            fdp_attribute=_normalize_text(field.fdp_attribute_name) or None,
            derivation_logic=_normalize_text(field.derivation_logic) or None,
            is_cde=field.is_cde.value if field.is_cde else None,
            product_zone=_normalize_text(field.product_zone) or None,
            sample_value_1=_normalize_text(field.sample_value_1) or None,
            sample_value_2=_normalize_text(field.sample_value_2) or None
        )

        create_column_from_model(
            atlas_client,
            column_model,
            table_qualified_name=table_model.qualified_name,
        )

    return table_model.qualified_name




def _create_lineage_processes(
    atlas_client: Any,
    model: CompleteDataProductModel,
    input_port_qualified_names: list[str] | None,
    output_port_qualified_name: str | None,
) -> None:
    """Create processes to represent data lineage: input ports -> data product -> output port."""
    data_product_qn = model.qualified_name
    data_product_name = model.basic_metadata.data_product_name
    
    # Process 1: Input ports -> Data Product (ingest process)
    if input_port_qualified_names:
        ingest_process_name = f"{data_product_name}_ingest_process"
        ingest_process = ProcessModel(
            process_name=ingest_process_name,
            query_id=ingest_process_name,
            query_text=f"Ingest lineage process for {data_product_name}",
        )
        input_refs = [("SCB_Table", qn) for qn in input_port_qualified_names]
        output_refs = [("SCB_DataProduct", data_product_qn)]
        create_process_from_model(
            atlas_client,
            ingest_process,
            input_refs=input_refs,
            output_refs=output_refs,
        )
    
    # Process 2: Data Product -> Output port (publish process)
    if output_port_qualified_name:
        publish_process_name = f"{data_product_name}_publish_process"
        publish_process = ProcessModel(
            process_name=publish_process_name,
            query_id=publish_process_name,
            query_text=f"Publish lineage process for {data_product_name}",
        )
        publish_input_refs = [("SCB_DataProduct", data_product_qn)]
        publish_output_refs = [("SCB_Table", output_port_qualified_name)]
        create_process_from_model(
            atlas_client,
            publish_process,
            input_refs=publish_input_refs,
            output_refs=publish_output_refs,
        )


def _create_input_port_assets(
    atlas_client: Any,
    model: CompleteDataProductModel,
    database_model: DatabaseModel | None = None,
) -> list[str]:
    input_ports = model.ports.data_product_input_ports if model.ports else None
    if not input_ports:
        return []

    database_model = database_model or _ensure_port_database(atlas_client, model)
    created_qns: list[str] = []
    for port in input_ports:
        normalized_name = _slugify_identifier(port)
        table_model = TableModel(
            table_name=normalized_name,
            database_name=database_model.database_name,
            description=f"Input port for data product {model.basic_metadata.data_product_name}",
            table_type=None,
            create_time=None,
            temporary=False,
            serde1=None,
            serde2=None,
        )
        create_table_from_model(
            atlas_client,
            table_model,
            database_qualified_name=database_model.qualified_name,
        )
        created_qns.append(table_model.qualified_name)

    return created_qns


def _to_int_or_raise(value: Any, *, field_name: str, strict: bool) -> int | None:
    text = _normalize_text(value)
    if not text:
        return None
    parsed = _to_int_or_none(value)
    if parsed is None and strict:
        raise ValueError(f"Invalid integer value '{text}' for '{field_name}'.")
    return parsed


def _normalize_mapped_value(value: Any, mapping: dict[str, str], *, field_name: str, strict: bool) -> str | None:
    text = _normalize_text(value)
    if not text:
        return None
    normalized_key = text.lower()
    if normalized_key in mapping:
        return mapping[normalized_key]
    if strict:
        raise ValueError(f"Invalid value '{text}' for '{field_name}'.")
    return text

def _find_sheet_name_by_alias(sheet_names: list[str], aliases: set[str]) -> str | None:
    for sheet_name in sheet_names:
        if _normalize_header(sheet_name) in aliases:
            return sheet_name
    return None

def _find_data_schema_sheet_name(sheet_names: list[str]) -> str | None:
    return _find_sheet_name_by_alias(sheet_names, _DATA_SCHEMA_SHEET_ALIASES)

def _find_data_product_sheet_name(sheet_names: list[str]) -> str | None:
    return _find_sheet_name_by_alias(sheet_names, _DATA_PRODUCT_SHEET_ALIASES)



def _extract_tabular_rows(data_sheet: pd.DataFrame, *, strict: bool = False) -> list[dict[str, Any]]:
    header_idx = None
    for idx in range(len(data_sheet)):
        row = data_sheet.iloc[idx]
        for value in row.tolist():
            if _normalize_header(value) == "data product name":
                header_idx = idx
                break
        if header_idx is not None:
            break

    if header_idx is None:
        raise ValueError("Could not locate header row containing 'Data Product Name'.")

    header_row = data_sheet.iloc[header_idx]
    # Ignore first column in the template; metadata starts from second column.
    headers = [_normalize_text(value) for value in header_row.tolist()[1:]]
    if strict:
        missing_headers = sorted(header for header in _STRICT_DATA_PRODUCT_REQUIRED_HEADERS if header not in headers)
        if missing_headers:
            raise ValueError(f"Missing required headers in Data Product sheet: {missing_headers}")

    rows: list[dict[str, Any]] = []
    for idx in range(header_idx + 1, len(data_sheet)):
        values = data_sheet.iloc[idx].tolist()[1:]
        row = {headers[i]: values[i] for i in range(min(len(headers), len(values))) if headers[i]}
        product_name = _normalize_text(row.get("Data Product Name"))
        if not product_name:
            continue
        rows.append(row)
    return rows


def _parse_schema_master_sheet(file_path: str | Path, sheet_name: str, *, strict: bool = False) -> dict[str, list[DataProductMasterSchema]]:
    raw_df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    header_idx = None
    for idx in range(len(raw_df)):
        row = [_normalize_header(v) for v in raw_df.iloc[idx].tolist()]
        if "column name" in row and "data type" in row:
            header_idx = idx
            break

    if header_idx is None:
        if strict:
            raise ValueError(
                f"Schema sheet '{sheet_name}' must contain a header row with 'Column Name' and 'Data Type'."
            )
        return []

    schema_fields: dict[str, DataProductMasterSchema] = dict()
    for idx in range(header_idx + 1, len(raw_df)):
        row = raw_df.iloc[idx].tolist()
        data_product = _normalize_text(row[1] if len(row) > 1 else "")
        id = _normalize_text(row[2] if len(row) > 2 else "")
        category = _normalize_text(row[3] if len(row) > 3 else "")
        attribute_name = _normalize_text(row[4] if len(row) > 4 else "")
        source_of_attribute = _normalize_text(row[5] if len(row) > 5 else "")
        field_name = _normalize_text(row[6] if len(row) > 6 else "")
        data_type = _normalize_text(row[7] if len(row) > 7 else "")
        is_direct_text = _normalize_text(row[8] if len(row) > 8 else "")
        field_description = _normalize_text(row[9] if len(row) > 9 else "")
        field_type = _normalize_text(row[10] if len(row) > 10 else "")
        current_source_attribute = _normalize_text(row[11] if len(row) > 11 else "")
        sudleger_ds = _normalize_text(row[12] if len(row) > 12 else "")
        fdp_attribute = _normalize_text(row[13] if len(row) > 13 else "")
        derivation_logic = _normalize_text(row[14] if len(row) > 14 else "")
        is_cde_text = _normalize_text(row[16] if len(row) > 15 else "")
        product_zone = _normalize_text(row[16] if len(row) > 16 else "")
        sample_value_1 = _normalize_text(row[17] if len(row) > 17 else "")
        sample_value_2 = _normalize_text(row[18] if len(row) > 18 else "")

        if not field_name:
            continue
        
        if data_product not in schema_fields:
            schema_fields[data_product] = []

        schema_fields[data_product].append(DataProductMasterSchema(
            id=id,
            category=category or None,
            attribute_name=attribute_name or None,
            source_of_attribute=source_of_attribute or None,
            field_name=field_name,
            data_type=data_type or None,
            direct_derived=is_direct_text or None,
            field_description=field_description or None,
            field_type=field_type or None,
            current_source_attribute=current_source_attribute or None,
            sudleger_ds=sudleger_ds or None,
            fdp_attribute=fdp_attribute or None,
            derivation_logic=derivation_logic or None,
            is_cde=_to_bool(is_cde_text) if is_cde_text else False,
            product_zone=product_zone or None,
            sample_value=sample_value_1 or None,
            sample_value_source=sample_value_2 or None
        ))

    if strict and not schema_fields:
        raise ValueError(f"Schema sheet '{sheet_name}' does not contain any schema field rows.")

    return schema_fields



def parse_master_schema_workbook_to_data_products(file_path: str | Path, *, strict: bool = False) -> list[CompleteDataProductModel]:
    """Parse workbook metadata into Pydantic data product models."""
    workbook_path = Path(file_path)
    if not workbook_path.exists():
        raise FileNotFoundError(f"File not found: {workbook_path}")

    xls = pd.ExcelFile(workbook_path)
    data_product_sheet = _find_data_product_sheet_name(xls.sheet_names)
    if not data_product_sheet:
        raise ValueError("Workbook must contain a 'Data Product' sheet.")
    
    schema_sheet = _find_data_schema_sheet_name(xls.sheet_names)
    if not schema_sheet:
        raise ValueError("Workbook must contain a 'Master Schema' sheet.")

    data_sheet = pd.read_excel(workbook_path, sheet_name=data_product_sheet, header=None)
    schema_definitions = _parse_schema_master_sheet(workbook_path, schema_sheet, strict=strict)
    
    rows = _extract_tabular_rows(data_sheet, strict=strict)
    if not rows:
        raise ValueError("No data product rows found in the Data Product sheet.")

    models: list[CompleteDataProductModel] = []
    for row in rows:
        product_name = _normalize_text(row.get("Data Product Name"))

        if product_name not in schema_definitions:
            if strict:
                raise ValueError(
                    f"Missing schema definition for data product '{product_name}' in Master Schema sheet."
                )
            schema_fields = []
        else:
            schema_fields = schema_definitions[product_name]

        model = CompleteDataProductModel(
            basic_metadata=DataProductBasicMetadata(
                data_product_name=product_name,
                description=_normalize_text(row.get("Description")),
                data_product_category=(
                    _normalize_mapped_value(
                        row.get("Data Product Category"),
                        _DATA_PRODUCT_CATEGORY_MAP,
                        field_name="Data Product Category",
                        strict=strict,
                    )
                    or "Source-Aligned"
                ),
                #granularity=_normalize_text(row.get("Granularity / Dimension")) or None,
                granularity=_normalize_mapped_value(
                    row.get("Granularity / Dimension"),
                    _GRANULARITY_MAP,
                    field_name="Granularity/De=imension",
                    strict=strict

                ) or None,
                tags=_to_tag_list(row.get("Tags/Keywords")) or None,
            ),
            business_metadata=DataProductBusinessMetadata(
                business_purpose=_normalize_text(row.get("Business Purpose")),
                gcfo_owner_name=_normalize_text(row.get("GFCO Owner")) or None,
                gcfo_owner_contact=_normalize_text(row.get("GFCO Owner Contact Information")) or None,
                linked_entities=_to_list(row.get("Linked Domain - Products / Entities")) or None,
            ),
            classification=DataProductClassification(
                sensitivity=SensitivityEnum(
                    _normalize_mapped_value(
                        row.get("Sensitivity"),
                        _SENSITIVITY_MAP,
                        field_name="Sensitivity",
                        strict=strict,
                    )
                    or SensitivityEnum.SENSITITY_INTERNAL.value
                ),
                personal=_to_bool_or_raise(row.get("Personal Data"), field_name="Personal Data", strict=strict),
                geo_location_access=_to_list(row.get("Geo Location Access")) or None,
                regulatory_flags=_to_list(row.get("Regulatory Flags")) or None,
                certifications=_to_list(row.get("Certifications")) or None,
                approval=_normalize_text(row.get("Approval")) or None,
            ),
            ports=DataProductPorts(
                data_product_input_ports=_to_list(
                    _first_non_empty(row, ["Source System(s)", "Source Systems", "Input Ports"])
                )
                or None,
                data_product_output_port=None,
                data_product_input_process=None,
                data_product_output_process=None,
                delivery_channels=_to_list(row.get("Delivery Channels")) or None,
                access_rules=_normalize_text(row.get("Access Rules")) or None,
                data_landing_pattern=_normalize_text(row.get("Data Landing Pattern")) or None,
                data_handshake=_normalize_text(row.get("Data Handshake")) or None,
            ),
            usage=DataProductUsage(
                users=_to_int_or_raise(row.get("Users"), field_name="Users", strict=strict),
                systems=_to_int_or_raise(row.get("Systems"), field_name="Systems", strict=strict),
                usecases=_to_list(row.get("Usecases")) or None,
            ),
            lifecycle=DataProductLifecycle(
                version=_normalize_text(row.get("Version")) or None,
                environment=_normalize_text(row.get("Life Cycle / Status")) or None,
                lifecycle_status=None,
                delivery_date=None,
            ),
            governance_metadata=DataProductGovernanceMetadata(
                domain=_normalize_text(row.get("Domain")),
                sub_domain=_normalize_text(row.get("Sub-Domain")),
                refresh_frequency=_normalize_mapped_value(
                    row.get("Refresh Frequency"),
                    _REFRESH_FREQUENCY_MAP,
                    field_name="Refresh Frequency",
                    strict=strict,
                ),
                refresh_cut=_normalize_mapped_value(
                    row.get("Refresh Cut"),
                    _REFRESH_CUT_MAP,
                    field_name="Refresh Cut",
                    strict=strict
                ),
                data_product_owner=_normalize_text(row.get("Source Domain Owner")) or None,
                data_product_owner_contact_information=_normalize_text(row.get("Source Domain Owner Contact Information")) or None,
                domain_owner=_normalize_text(row.get("Source Domain Owner")) or None,
                domain_owner_contact_information=_normalize_text(row.get("Source Domain Owner Contact Information")) or None,
                data_steward=_normalize_text(row.get("Data Steward")) or None,
                data_steward_contact_information=_normalize_text(row.get("Steward Contact Information")) or None,
                support_contact=_normalize_text(row.get("Support Contact")) or None,
                support_contact_information=_normalize_text(row.get("Support Contact Information")) or None,
                data_retention=_normalize_text(row.get("Data Retention")) or None,
                sla=_normalize_text(row.get("Agreed SLA")) or None,
                communication_channel=_to_list(row.get("Communication Channel")) or None,
            ),
            output_port_schema=schema_fields or None,
        )
        models.append(model)

    return models


def parse_master_schema_sheet(file_path: str | Path) -> list[DataProductMasterSchema]:
    """Parse schema fields for a data product from a specified workbook sheet."""
    
    workbook_path = Path(file_path)
    if not workbook_path.exists():
        raise FileNotFoundError(f"File not found: {workbook_path}")

    xls = pd.ExcelFile(workbook_path)
    data_product_sheet = _find_data_product_sheet_name(xls.sheet_names)
    if not data_product_sheet:
        raise ValueError("Workbook must contain a 'Data Product' sheet.")

    master_schema_sheet = _find_data_schema_sheet_name(xls.sheet_names)
    schema_def = _parse_schema_master_sheet(workbook_path, master_schema_sheet) if master_schema_sheet else []

    return schema_def

def create_data_products_from_workbook(
    file_path: str | Path,
    atlas_client: Any,
    *,
    strict: bool = False,
) -> list[str]:
    """Create Data Product entities in Atlas from workbook metadata."""
    models = parse_master_schema_workbook_to_data_products(file_path, strict=strict)
    created: list[str] = []
    for model in models:
        input_database_model = _ensure_port_database(atlas_client, model)
        input_port_qualified_names = _create_input_port_assets(
            atlas_client,
            model,
            database_model=input_database_model,
        )

        output_database_model = _ensure_port_database(atlas_client, model)
        output_port_qualified_name = _create_output_port_assets(
            atlas_client,
            model,
            database_model=output_database_model,
        )
        create_data_product_from_model(
            atlas_client,
            model,
            input_port_qualified_names=input_port_qualified_names or None,
            output_port_qualified_name=output_port_qualified_name,
        )
        # Create lineage processes: input ports -> data product -> output port
        _create_lineage_processes(
            atlas_client,
            model,
            input_port_qualified_names,
            output_port_qualified_name,
        )
        created.append(model.basic_metadata.data_product_name)
    return created


def validate_metadata_workbook(file_path: str | Path, *, strict: bool = False) -> bool:
    """Validate workbook contains required sheets and at least one data product row."""
    #models = parse_workbook_to_data_products(file_path, strict=strict)
    models = parse_master_schema_workbook_to_data_products(file_path, strict=strict)
    return len(models) > 0
