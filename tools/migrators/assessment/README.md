# Assessment migrator

Rust scaffold for upgrading assessment bundles from `0.11.3` to `0.12.1`.
This is not implemented yet: running the binary exits with an error and writes nothing.

## First milestone

Implement `migrate_bundle` in `src/lib.rs`:

1. Check that the input is a JSON object with `format_version` set to `0.11.3`.
2. Return a copy with the version changed to `0.12.1`; preserve all other values.
3. Return an error for missing, malformed, or unsupported versions.
4. Run `cargo test` and enable the ignored test as you implement it.

Then implement a CLI with explicit input and output paths, preventing accidental
overwrite of the input. Validate real outputs against the canonical schema and run
the linter with both spec paths explicitly supplied. Passing validation alone does
not prove the newer grading rules have identical semantics.

The source corpus is `~/.hermes/cache/scratch/ppw-course/`. Leave it untouched;
write any migrated copies elsewhere in scratch. Preserve the private answer key.
