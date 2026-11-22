# ECC Codex skills

This repository is a curated local skill collection for Codex. Canonical skill
directories live in `skills/`; `skills.json` defines installation profiles.

- Preserve the Go, JavaScript/TypeScript, Rust 2024, Zig, Swift/SwiftUI, and Haskell scope.
- Keep skill descriptions precise and entrypoints compact. Put substantial,
  conditional examples in linked references; keep essential invariants inline.
- Use only tools available in the current Codex session. Do not invent APIs,
  require provider-specific agent names, or install global hooks.
- Optional plugins live under `plugins/`, with a catalog and a native marketplace
  at `.agents/plugins/marketplace.json`. Install them only in explicit plugin mode
  through Codex's own CLI; never copy account state, credentials, or private caches.
- Respect each target project's toolchain, MSRV, lint policy, and test commands.
- Installer changes must preserve foreign skills and reject conflicts before
  changing any links. Test in temporary directories, never the real home.
- Plugin tests must use a simulated CLI. Do not install or connect real account
  plugins while testing the installer. Preserve pre-existing enabled/disabled state.
- Verify with `python3 -m unittest discover -s tests -v` and
  `python3 scripts/validate.py`. No dependency installation is needed.

`install.sh` is a POSIX shell entrypoint to the Python standard-library installer.
Do not add dependencies solely for skill installation or validation.
