//! Composable, version-specific upgrades for assessment bundles.

use serde_json::Value;

/// One explicitly supported upgrade between assessment format versions.
pub struct Migration {
    pub from: &'static str,
    pub to: &'static str,
    pub apply: fn(&Value) -> Result<Value, String>,
}

/// Upgrade a 0.11.3 bundle to 0.12.1 without changing its other content.
/// Reject malformed input or a different source version; leave the input untouched.
pub fn v0_11_3_to_v0_12_1(input: &Value) -> Result<Value, String> {
    let mut bundle = input.clone();

    let version = bundle
        .get_mut("format_version")
        .ok_or("No version property found")?;

    match version.as_str() {
        Some("0.11.3") => {
            *version = Value::String("0.12.1".into());
            Ok(bundle)
        },
        Some(ver) => Err(format!("Expected version 0.11.3, got {ver}")),
        None => Err("format_version must be a string".into())
    }
}

/// Select an ordered chain of registered upgrades from `source` to `target`.
/// Return an error when no unambiguous chain exists; never silently downgrade.
/// A supported source equal to the target needs no steps.
pub fn migration_path<'a>(
    _source: &str,
    _target: &str,
    _migrations: &'a [Migration],
) -> Result<Vec<&'a Migration>, String> {
    todo!("find and validate the migration chain")
}

/// Read the bundle's source version and apply the registered steps to `target`.
/// Return an error for malformed input or an unsupported path; do not mutate input.
pub fn migrate_bundle(_input: &Value, _target: &str) -> Result<Value, String> {
    // TODO: register 0.11.3 -> 0.12.1 and compose the selected migrations.
    todo!("route and apply migrations")
}
