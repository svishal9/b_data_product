from .base import BaseEnumCategory

scb_domain_enums = BaseEnumCategory(
    atlas_name="SCB_Domain",
    atlas_description="Domain of the data product",
    element_defs = [
        { "value": "FM",  "ordinal": 1 },
        { "value": "CIB-Banking",  "ordinal": 2 },
        { "value": "WRB-Banking",  "ordinal": 3 },
    ]
)

scb_sub_domains_enums = BaseEnumCategory(
    atlas_name="SCB_SubDomain",
    atlas_description="Sub-Domain of the data product",
    element_defs = [
        { "value": "FX",  "ordinal": 1 },
        { "value": "RATES",  "ordinal": 2 },
        { "value": "Options",  "ordinal": 3 },
        { "value": "FM Common", "ordinal": 4},
        { "value": "Loans", "ordinal": 5},
        { "value": "Money Market", "ordinal": 6},
        { "value": "Swaps", "ordinal": 7},
        { "value": "Bonds", "ordinal": 8},
        { "value": "Derivatives", "ordinal": 9},
        { "value": "Commodities", "ordinal": 10},
        { "value": "Credit", "ordinal": 11},
        { "value": "Lending", "ordinal": 12},
        { "value": "Trade Finance", "ordinal": 13},
        { "value": "Cash Management", "ordinal": 14},
        { "value": "Retail Landing", "ordinal": 15},
        { "value": "Wealth Management", "ordinal": 16}, 
        { "value": "Cusotmer Deposits", "ordinal": 17}, 
        { "value": "Retail & Corporate Cards", "ordinal": 18}, 
        { "value": "Custody Services", "ordinal": 19}, 
        { "value": "CIB - Reference Static", "ordinal": 20}, 
        { "value": "Wealth Management", "ordinal": 21} 
    ]
)

scb_sensitivity = BaseEnumCategory(
    atlas_name="SCB_Sensitivity",
    atlas_description="Sensitivity of the data product",
    element_defs = [
        { "value": "Internal", "ordinal": 1 },
        { "value": "External", "ordinal": 2 }
    ]
)

scb_data_product_category = BaseEnumCategory(
    atlas_name="SCB_DataProductCategory",
    atlas_description="Category of the data product",
    element_defs = [
        { "value": "Source-Aligned",  "ordinal": 1 },
        { "value": "Consumer-Aligned",  "ordinal": 2 }
    ]
)

scb_environment = BaseEnumCategory(
    atlas_name="SCB_Environment",
    atlas_description="LifeCycle Status of the data product",
    element_defs = [
        { "value": "Production",  "ordinal": 1 }
    ]
)

scb_granularity = BaseEnumCategory(
    atlas_name="SCB_Granularity",
    atlas_description="Granularity of the data product",
    element_defs = [
        { "value": "Trade",  "ordinal": 1 },
        { "value": "Trade + Legs",  "ordinal": 2 },
        { "value": "Incremental", "ordinal": 3},
        { "value": "Portfolio", "ordinal": 4},
        { "value": "Contract", "ordinal": 5},
        { "value": "Transaction", "ordinal": 6},
        { "value": "Account", "ordinal": 7},
        { "value": "Incremental", "ordinal": 8}

    ]
)

scb_refresh_cut = BaseEnumCategory(
    atlas_name="SCB_RefreshCut",
    atlas_description="Refresh Cut of the data product",
    element_defs = [
        { "value": "Actual", "ordinal": 1 }
    ]
)

scb_refresh_frequency = BaseEnumCategory(
    atlas_name="SCB_RefreshFrequency",
    atlas_description="Refresh Frequency of the data product",
    element_defs = [
        { "value": "Daily (T+0)", "ordinal": 1 }
    ]
)

enum_names = [
    scb_data_product_category.atlas_name,
    scb_domain_enums.atlas_name,
    scb_environment.atlas_name,
    scb_granularity.atlas_name,
    scb_refresh_cut.atlas_name,
    scb_refresh_frequency.atlas_name,
    scb_sensitivity.atlas_name,
    scb_sub_domains_enums.atlas_name
]

all_enums = [
    scb_data_product_category.prepare_atlas_type_definition(),
    scb_domain_enums.prepare_atlas_type_definition(),
    scb_environment.prepare_atlas_type_definition(),
    scb_granularity.prepare_atlas_type_definition(),
    scb_refresh_cut.prepare_atlas_type_definition(),
    scb_refresh_frequency.prepare_atlas_type_definition(),
    scb_sensitivity.prepare_atlas_type_definition(),
    scb_sub_domains_enums.prepare_atlas_type_definition()
]