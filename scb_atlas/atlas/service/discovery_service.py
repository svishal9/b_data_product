import logging

from apache_atlas.client.base_client import AtlasClient

logger = logging.getLogger(__name__)

DEFAULT_LIMIT = 2 
DEFAULT_OFFSET = 0
DEFAULT_EXCLUDE_DELETE = True

def _quote(v: str) -> str:
    return "'" + str(v).replace("'", "\\'") + "'"

def basic_search(
        atlas_client: AtlasClient, 
        names: list[str],
        type_name: str = "DataSet",
    ) -> list[dict] | None:

    """
    Performs a basic search for entities in Apache Atlas.

    Args:
        atlas_client (AtlasClient): The client to use for communicating with the Atlas server.
        names (list[str]): A list of names to search for.
        type_name (str, optional): The type of entity to search for. Defaults to "DataSet".

    Returns:
        list[dict] | None: A list of dictionaries representing the matching entities, or None if no matches are found.

    Raises:
        AtlasClientError: If an error occurs while communicating with the Atlas server.
    """
    entity_retrieved = []
    try:
        all_names = ",".join(_quote(name) for name in names)
        dsl_query = f"FROM {type_name} WHERE name =[{all_names}]"
        result = atlas_client.discovery.basic_search(
            type_name=type_name,
            classification="",
            query=dsl_query,
            exclude_deleted_entities=True
        )

        if result.entities:
            print(f"{len(result.entities)} entity found in database.")

            for entity in result.entities:
                entity_retrieved.append({
                    "guid": entity["guid"],
                    "type_name": entity["typeName"],
                    "name": entity["attributes"].get("name", ""),
                    "qualified_name": entity["attributes"]["qualifiedName"]
                })
        return entity_retrieved
    except Exception:
        logger.exception("query: '%s' failed in basic search")
        return None


def dsl_search(
        atlas_client: AtlasClient, 
        names: list[str],
        type_name: str = "DataSet",
    ) -> list[dict] | None:

    """
    Performs a DSL-based search for entities in Apache Atlas.

    Args:
        atlas_client (AtlasClient): The client to use for communicating with the Atlas server.
        names (list[str]): A list of names to search for.
        type_name (str, optional): The type of entity to search for. Defaults to "DataSet".

    Returns:
        list[dict] | None: A list of dictionaries representing the matching entities, or None if no matches are found.

    Raises:
        AtlasClientError: If an error occurs while communicating with the Atlas server.
    """
    entity_retrieved = []
    try:
        all_names = ",".join(_quote(name) for name in names)
        dsl_query = f"FROM {type_name} WHERE name =[{all_names}]"
        result = atlas_client.discovery.dsl_search(dsl_query)

        if result.entities:
            print(f"{len(result.entities)} entity found in database.")

            for entity in result.entities:
                entity_retrieved.append({
                    "guid": entity["guid"],
                    "type_name": entity["typeName"],
                    "name": entity["attributes"].get("name", ""),
                    "qualified_name": entity["attributes"]["qualifiedName"]
                })
        return entity_retrieved
    except Exception:
        logger.exception("query: '%s' failed in basic search")
        return None

def process_search(atlas_client: AtlasClient, type_name: str):

    entity_retrieved = []
    try:
        dsl_query = f"FROM {type_name}"
        result = atlas_client.discovery.dsl_search(dsl_query)

        if result.entities:
            print(f"{len(result.entities)} entity found in database.")

            for entity in result.entities:
                entity_retrieved.append({
                    "guid": entity["guid"],
                    "type_name": entity["typeName"],
                    "name": entity["attributes"].get("name", ""),
                    "qualified_name": entity["attributes"]["qualifiedName"]
                })
        return entity_retrieved
    except Exception:
        logger.exception("query: '%s' failed in basic search")
        return None