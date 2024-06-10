from __future__ import annotations

from typing import Final

from django.db import migrations

VALIDATION_FUNCTION_SQL: Final = """
CREATE OR REPLACE FUNCTION validate_json(input_json jsonb, schema_json json) RETURNS boolean LANGUAGE plrust AS $$
[dependencies]
valico = "3.6.0"
serde_json = "1.0"
serde = "1.0"
[code]
use valico::json_schema::{self, Scope};
use serde_json::{Value, json};
use std::str::FromStr;

let input_json_str = serde_json::to_string(&input_json).unwrap();
let schema_json_str = serde_json::to_string(&schema_json).unwrap();

let input: Value = serde_json::from_str(&input_json_str).unwrap();
let schema: Value = serde_json::from_str(&schema_json_str).unwrap();

let mut scope = Scope::new();

let schema = scope.compile_and_return(schema, false).unwrap();

match schema.validate(&input).is_valid() {
    true => Ok(Some(true)),
    false => Ok(Some(false)),
}
$$;
"""


class Migration(migrations.Migration):
    intiial = True

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION plrust;", reverse_sql="DROP EXTENSION plrust;"
        ),
        migrations.RunSQL(
            sql=VALIDATION_FUNCTION_SQL,
            reverse_sql="DROP FUNCTION validate_json(json, json);",
        ),
    ]
