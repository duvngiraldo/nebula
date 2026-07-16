EXPECTED_SCHEMAS: dict[str, list[str]] = {
    "lead": [
        "id", "id_persona", "id_usuario", "estado", "estado_contrato",
        "formulario_de_origen", "origen_lead", "lead_type", "importe_contrato",
        "fecha_de_creacion", "fecha_de_cierre", "is_soft_delete", "visible_tabla",
    ],
    "call": [
        "id", "id_lead", "id_usuario", "id_persona", "numero",
        "tipo_de_llamada", "timestamp_connection", "timestamp_call_end",
        "id_call_connect", "is_soft_delete",
    ],
    "person": ["id", "telefono_movil", "email", "dni", "nombre"],
    "user": ["id", "email", "nombre"],
}


def get_expected_columns(table: str) -> list[str]:
    return EXPECTED_SCHEMAS[table]
