//! Composable, version-specific upgrades for assessment bundles.

use imbl::HashMap;
use itertools::Itertools;
use semver::Version;
use serde_json::Value;

/// One explicitly supported upgrade between assessment format versions.
pub struct Migration {
    pub from: &'static Version,
    pub to: &'static Version,
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
        }
        Some(ver) => Err(format!("Expected version 0.11.3, got {ver}")),
        None => Err("format_version must be a string".into()),
    }
}

fn get_assessment_version(input: &Value) -> Result<&str, String> {
    Ok(input
        .get("format_version")
        .ok_or("No version property found")?
        .as_str()
        .ok_or("format_version must be a string")?)
}

type Best<'a> = (usize, Option<&'a Migration>);

/// Select an ordered chain of registered upgrades from `source` to `target`.
/// Return an error when no chain exists; never silently downgrade.
/// Equal source and target versions need no steps, even when unregistered.
/// Prefer the longest chain; for equally long chains, prefer the smaller next
/// version. Duplicate steps with the same endpoints retain their input order.
pub fn migration_path<'a>(
    source: &Version,
    target: &Version,
    migrations: &'a [Migration],
) -> Result<Vec<&'a Migration>, String> {
    if source == target {
        return Ok(vec![]);
    }

    if let Some(m) = migrations.iter().find(|m| m.from >= m.to) {
        return Err(format!("Invalid migration: {} -> {}", m.from, m.to));
    }

    let best = migrations
        .iter()
        .filter(|m| m.from >= source && m.to <= target)
        .sorted_by(|a, b| b.from.cmp(a.from))
        .fold(
            HashMap::<&Version, Best<'a>>::new().update(target, (0, None)),
            |best, m| {
                let Some(&(length, _)) = best.get(m.to) else {
                    return best;
                };

                let candidate_len = length + 1;

                let better = match best.get(m.from) {
                    None => true,
                    Some(&(old_len, Some(old))) => {
                        candidate_len > old_len || (candidate_len == old_len && m.to < old.to)
                    }
                    Some(&(old_len, None)) => candidate_len > old_len,
                };

                if better {
                    best.update(m.from, (candidate_len, Some(m)))
                } else {
                    best
                }
            },
        );

    let (_, first) = best
        .get(source)
        .ok_or(format!("No migration path from {source} to {target}"))?;

    Ok(std::iter::successors(*first, |m| best.get(m.to).and_then(|(_, next)| *next)).collect())
}

/// Read the bundle's source version and apply the registered steps to `target`.
/// Return an error for malformed input or an unsupported path; do not mutate input.
pub fn migrate_bundle(_input: &Value, _target: &str) -> Result<Value, String> {
    // TODO: register 0.11.3 -> 0.12.1 and compose the selected migrations.
    todo!("route and apply migrations")
}
