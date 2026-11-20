use std::sync::LazyLock;

use assessment_migrator::{Migration, migration_path};
use semver::Version;
use serde_json::Value;

static V1: LazyLock<Version> = LazyLock::new(|| Version::new(0, 11, 3));
static V2: LazyLock<Version> = LazyLock::new(|| Version::new(0, 12, 1));
static V3: LazyLock<Version> = LazyLock::new(|| Version::new(0, 12, 2));
static V4: LazyLock<Version> = LazyLock::new(|| Version::new(0, 13, 0));

fn unchanged(input: &Value) -> Result<Value, String> {
    Ok(input.clone())
}

fn step(from: &'static Version, to: &'static Version) -> Migration {
    Migration {
        from,
        to,
        apply: unchanged,
    }
}

#[test]
fn finds_connected_steps_in_order_even_when_registry_is_unsorted() {
    let steps = [step(&V2, &V3), step(&V1, &V2)];
    let path = migration_path(&V1, &V3, &steps).unwrap();
    let endpoints: Vec<_> = path.iter().map(|m| (m.from, m.to)).collect();
    assert_eq!(endpoints, vec![(&*V1, &*V2), (&*V2, &*V3)]);
}

#[test]
fn rejects_gaps_and_downgrades() {
    let steps = [step(&V1, &V2), step(&V3, &V4)];
    assert!(migration_path(&V1, &V4, &steps).is_err());
    assert!(migration_path(&V2, &V1, &steps).is_err());
}

#[test]
fn prefers_a_longer_path_over_a_direct_step() {
    let steps = [step(&V1, &V3), step(&V1, &V2), step(&V2, &V3)];
    let path = migration_path(&V1, &V3, &steps).unwrap();
    assert_eq!(path.len(), 2);
    assert_eq!(path[0].to, &*V2);
    assert_eq!(path[1].to, &*V3);
}

#[test]
fn breaks_equal_length_ties_by_smaller_next_version() {
    let steps = [
        step(&V1, &V3),
        step(&V3, &V4),
        step(&V1, &V2),
        step(&V2, &V4),
    ];
    let path = migration_path(&V1, &V4, &steps).unwrap();
    assert_eq!(path.len(), 2);
    assert_eq!(path[0].to, &*V2);
    assert_eq!(path[1].to, &*V4);
}

#[test]
fn duplicate_endpoints_keep_the_first_registered_step() {
    let steps = [step(&V1, &V2), step(&V1, &V2)];
    let path = migration_path(&V1, &V2, &steps).unwrap();
    assert_eq!(path.len(), 1);
    assert!(std::ptr::eq(path[0], &steps[0]));
}

#[test]
fn equal_unregistered_versions_are_a_noop() {
    assert!(migration_path(&V1, &V1, &[]).unwrap().is_empty());
}

#[test]
fn rejects_non_forward_registered_steps() {
    for steps in [[step(&V2, &V1)], [step(&V1, &V1)]] {
        assert!(migration_path(&V1, &V2, &steps).is_err());
    }
}
