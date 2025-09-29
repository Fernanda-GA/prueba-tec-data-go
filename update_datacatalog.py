
"""
update_datacatalog.py
Lee un YAML de metadatos y:
 - actualiza la descripción del Entry correspondiente en Data Catalog
 - crea (si no existe) una TagTemplate y añade un Tag al Entry


"""

import os
import sys
import yaml
from google.cloud import datacatalog_v1
from google.api_core.exceptions import NotFound, AlreadyExists
from google.protobuf.field_mask_pb2 import FieldMask

# Configs: lee variables de entorno
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("PROJECT_ID")
DATASET_ID = os.environ.get("DATASET_ID")
TAG_TEMPLATE_LOCATION = os.environ.get("TAG_TEMPLATE_LOCATION", "us")
TAG_TEMPLATE_ID = "deacero_metadata"  

if not PROJECT_ID or not DATASET_ID:
    print("ERROR: define las variables de entorno GOOGLE_CLOUD_PROJECT y DATASET_ID")
    sys.exit(1)

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def tag_template_full_name(project_id, location, template_id):
    return f"projects/{project_id}/locations/{location}/tagTemplates/{template_id}"

def tag_template_parent(project_id, location):
    return f"projects/{project_id}/locations/{location}"

def ensure_tag_template(client, project_id, location, template_id):
    name = tag_template_full_name(project_id, location, template_id)
    try:
        tmpl = client.get_tag_template(name=name)
        print(f"Tag template existente: {name}")
        return tmpl
    except NotFound:
        print(f"Creando tag template: {name}")
        # Definimos dos campos: data_steward (string) y labels (string, con tags separadas por coma)
        tag_template = datacatalog_v1.types.TagTemplate()
        tag_template.display_name = "Deacero metadata"
        tag_template.fields["data_steward"] = datacatalog_v1.types.TagTemplateField(
            display_name="Data steward",
            type_=datacatalog_v1.types.FieldType(primitive_type=datacatalog_v1.types.FieldType.PrimitiveType.STRING),
        )
        tag_template.fields["labels"] = datacatalog_v1.types.TagTemplateField(
            display_name="Labels (comma-separated)",
            type_=datacatalog_v1.types.FieldType(primitive_type=datacatalog_v1.types.FieldType.PrimitiveType.STRING),
        )
        parent = tag_template_parent(project_id, location)
        try:
            created = client.create_tag_template(
                parent=parent,
                tag_template_id=template_id,
                tag_template=tag_template
            )
            print(f"Tag template creado: {created.name}")
            return created
        except AlreadyExists:
            return client.get_tag_template(name=name)

def find_entry_for_table(client, project_id, dataset_id, table_id):
    # linked_resource pra BigQuery table
    linked_resource = f"//bigquery.googleapis.com/projects/{project_id}/datasets/{dataset_id}/tables/{table_id}"
    try:
        entry = client.lookup_entry(request={"linked_resource": linked_resource})
        return entry
    except NotFound:
        print(f"Entry no encontrado para linked_resource={linked_resource}")
        return None

def update_entry_description(client, entry, new_description):
    if not entry:
        return False
    entry_update = datacatalog_v1.types.Entry()
    entry_update.name = entry.name
    entry_update.description = new_description
    client.update_entry(entry=entry_update, update_mask=FieldMask(paths=["description"]))
    print(f"Descripción actualizada para: {entry.name}")
    return True

def tag_exists_for_entry(client, entry_name, tag_template_name):
    for t in client.list_tags(parent=entry_name):
        if t.template == tag_template_name:
            return True
    return False

def create_tag_for_entry(client, entry_name, tag_template_name, data_steward, labels):
    # labels: lista -> lo guardamos como string separado por coma
    if tag_exists_for_entry(client, entry_name, tag_template_name):
        print(f"Entry {entry_name} ya tiene tag con template {tag_template_name} (se ignora creación).")
        return None
    tag = datacatalog_v1.types.Tag()
    tag.template = tag_template_name
    tag.fields["data_steward"] = datacatalog_v1.types.TagField()
    tag.fields["data_steward"].string_value = data_steward
    tag.fields["labels"] = datacatalog_v1.types.TagField()
    tag.fields["labels"].string_value = ", ".join(labels)
    created = client.create_tag(parent=entry_name, tag=tag)
    print(f"Tag creado: {created.name} en {entry_name}")
    return created

def main(yaml_path):
    data = load_yaml(yaml_path)
    tables = data.get("tables", [])
    if not tables:
        print("No hay tablas definidas en el YAML.")
        return

    dc = datacatalog_v1.DataCatalogClient()

    # 1) asegurar tag template
    template = ensure_tag_template(dc, PROJECT_ID, TAG_TEMPLATE_LOCATION, TAG_TEMPLATE_ID)
    tag_template_name = tag_template_full_name(PROJECT_ID, TAG_TEMPLATE_LOCATION, TAG_TEMPLATE_ID)

    # 2) por cada tabla: buscar entry, actualizar descripción y crear tag
    for t in tables:
        table_id = t.get("table_id")
        if not table_id:
            print("Saltando item sin table_id.")
            continue

        print("----")
        print(f"Procesando tabla: {table_id}")

        entry = find_entry_for_table(dc, PROJECT_ID, DATASET_ID, table_id)
        if entry is None:
            print(f"  → Entry no encontrado para {table_id}. Verifica que Dataplex/Datacatalog haya hecho discovery y que la vista/tabla exista en {PROJECT_ID}.{DATASET_ID}.{table_id}")
            continue

        # actualizar descripción
        desc = t.get("description", "")
        if desc:
            update_entry_description(dc, entry, desc)

        # crear tag
        steward = t.get("data_steward", "")
        tags = t.get("tags", [])
        create_tag_for_entry(dc, entry.name, tag_template_name, steward, tags)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 update_datacatalog.py metadata.yaml")
        sys.exit(1)
    yaml_path = sys.argv[1]
    main(yaml_path)
