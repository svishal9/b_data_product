from .base import BaseClassificationCategory

scb_personal = BaseClassificationCategory(atlas_name="SCB Personal")
scb_internal = BaseClassificationCategory(atlas_name="SCB Sensitive Internal")
scb_external = BaseClassificationCategory(atlas_name="SCB Sensitive External")

classification_names = [
    scb_personal.atlas_name,
    scb_internal.atlas_name,
    scb_external.atlas_name
]

all_classifications = [
    scb_external.prepare_atlas_type_definition(),
    scb_internal.prepare_atlas_type_definition(),
    scb_personal.prepare_atlas_type_definition()
]