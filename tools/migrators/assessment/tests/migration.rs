use assessment_migrator::{migrate_bundle, v0_11_3_to_v0_12_1};
use serde_json::json;

#[test]
fn first_step_upgrades_without_changing_other_fields_or_input() {
    let input = json!({
        "format_version": "0.11.3",
        "assessment": {"id": "example"},
        "answer_key": {"q1": {"reference_answer": "private"}}
    });
    let original = input.clone();
    let expected = json!({
        "format_version": "0.12.1",
        "assessment": {"id": "example"},
        "answer_key": {"q1": {"reference_answer": "private"}}
    });

    assert_eq!(v0_11_3_to_v0_12_1(&input).unwrap(), expected);
    assert_eq!(input, original);
}

#[test]
fn first_step_rejects_invalid_versions_and_non_objects() {
    for input in [
        json!({"format_version": "0.10.0"}),
        json!({"format_version": 42}),
        json!({}),
        json!([]),
    ] {
        assert!(v0_11_3_to_v0_12_1(&input).is_err());
    }
}

#[test]
#[ignore = "enable when migrate_bundle is implemented"]
fn upgrades_version_without_changing_content() {
    let input = json!({
        "format_version": "0.11.3",
        "assessment": {"id": "example"},
        "answer_key": {"q1": {"reference_answer": "private"}}
    });
    let expected = json!({
        "format_version": "0.12.1",
        "assessment": {"id": "example"},
        "answer_key": {"q1": {"reference_answer": "private"}}
    });
    assert_eq!(migrate_bundle(&input, "0.12.1").unwrap(), expected);
    assert_eq!(input["format_version"], "0.11.3");
}

#[test]
#[ignore = "enable when migrate_bundle is implemented"]
fn rejects_unsupported_or_missing_version() {
    assert!(migrate_bundle(&json!({"format_version": "0.10.0"}), "0.12.1").is_err());
    assert!(migrate_bundle(&json!({}), "0.12.1").is_err());
    assert!(migrate_bundle(&json!([]), "0.12.1").is_err());
}
