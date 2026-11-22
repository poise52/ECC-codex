# Sources and curation

- ECC upstream snapshot: Git commit `b38be6a7` (the original checkout in this
  directory). The upstream MIT license is retained in [LICENSE](LICENSE).
- Go, TypeScript, Vue/Nuxt, React, backend/API, Playwright, accessibility,
  application security, PostgreSQL/migrations, Docker, and optimization
  references are adapted from the corresponding upstream `skills/` directories.
  Entry instructions, discovery names, routing, and installation were revised
  for this curated Codex collection. This is not the full upstream ECC plugin.
- Rust material was supplied by the user in the sibling `bol/` directory.
  Its technical topics were consolidated and reviewed for Rust 2024 and Codex.
  No separate license was supplied with `bol`; the upstream ECC MIT file does
  not establish redistribution rights for the user's separate Rust material.
- React performance attribution to Vercel Labs and PostgreSQL attribution to
  Supabase remain in their reference files.
- Zig guidance and the installer/validator were added in this curation.

## Swift and SwiftUI sources

The `swift` profile adapts the original ECC skills `swift-concurrency-6-2`,
`swift-actor-persistence`, `swift-protocol-di-testing`, and `swiftui-patterns`
from commit `b38be6a7`. It also incorporates selected guidance from Paul Hudson's
MIT-licensed skills, inspected on 2026-11-07:

| Source | Pinned commit | Local skill and retained license |
| --- | --- | --- |
| [SwiftUI Agent Skill / SwiftUI Pro](https://github.com/twostraws/SwiftUI-Agent-Skill) | `f2920b63995263f57b3e198674e89a602efba6d2` | [ecc-swiftui](skills/ecc-swiftui/SKILL.md), [MIT license](skills/ecc-swiftui/LICENSE) |
| [Swift Concurrency Agent Skill](https://github.com/twostraws/Swift-Concurrency-Agent-Skill) | `bee3f69ba17142da148d3c5406f148ed62592b69` | [ecc-swift](skills/ecc-swift/SKILL.md), [MIT license](skills/ecc-swift/LICENSE) |
| [Swift Testing Agent Skill](https://github.com/twostraws/Swift-Testing-Agent-Skill) | `2d6bba14a3c8bf3694f218b92fffe617c41ae43e` | [ecc-swift-testing](skills/ecc-swift-testing/SKILL.md), [MIT license](skills/ecc-swift-testing/LICENSE) |

[Swift-Agent-Skills](https://github.com/twostraws/Swift-Agent-Skills) is the
discovery directory used to find the concurrency and testing repositories;
it is not imported as another installed skill collection. Other directory
entries, such as SwiftData and App Store tools, are not bundled here.

The local references are condensed adaptations, not unmodified upstream
entrypoints. Scope is selected by task; there is no mandatory load-all review,
automatic SDK/language-mode upgrade, dependency installation, or assumed
deployment target. The persistence example commits its cache after a successful
write, the mutable test double is actor-isolated, and concurrency guidance
distinguishes optional module settings, reentrancy, cancellation, and stream
termination. Existing XCTest, ObservableObject, AppKit/UIKit, and synchronous
interop remain valid where the target project requires them.

Validation for this addition used Apple Swift 6.4: extracted non-UI examples
compiled with Swift 6 strict concurrency and warnings as errors, and also
typechecked with MainActor default isolation plus
`NonisolatedNonsendingByDefault`. Fourteen direct runtime scenarios checked
persistence, failed commits, concurrent writes, cancellation, overflow, injected
data/errors, finite stream ordering, and identifier handling. The SwiftUI sample
and macro-based Swift Testing suite could not be fully validated because the
installed Command Line Tools lacked `SwiftUIMacros` and `TestingMacros` plugins.
No UI-runner or macro-test success is claimed.

## Haskell sources

The `haskell` profile adapts [mightybyte/haskell-skill](https://github.com/mightybyte/haskell-skill)
at commit `2c34b722a43d9fae0923ba239acfd8400e929bfb`, inspected on 2026-11-11.
The original `haskell-coder` and `haskell-reviewer` entrypoints and selected
performance, effects, Cabal, and extension references were consolidated into
[ecc-haskell](skills/ecc-haskell/SKILL.md). Doug Beardsley's BSD-3-Clause notice
and terms are retained in the skill's [LICENSE](skills/ecc-haskell/LICENSE).

The six local references are edited adaptations. They preserve project-specific
compiler/build/formatting choices, distinguish transformer order from shared
mutation, and do not require ReaderT, textual errors, a fixed extension list,
whole-module imports, or an author-specific record naming scheme. Performance
guidance corrects the Text encoding/length and Criterion evaluation-depth
claims. No automatic learning capture, upstream PR workflow, alignment checker,
or unimplemented model-eval CI job is imported.

The upstream eval prompts were read as review material, not executed as a model
evaluation. Local structural/install checks and compiled example behavior do
not establish that Codex will select the skill correctly for every request.

The four complete local example modules were compiled with GHC 9.10.3,
Haskell2010, `-Wall -Werror`. Sixteen runtime scenarios checked constructor
bounds/roundtrips, transformer-order results, concurrent STM updates, WHNF versus
NF, and strict accumulation. A negative compilation check confirmed that the
hidden constructor cannot be called from another module. No additional Haskell
packages were installed; no QuickCheck/Hspec or Criterion runner is claimed.

## Optional plugins

The plugin catalog was captured on 2026-11-22 using native Codex CLI
`0.171.0-alpha.13` plugin/marketplace inventory, Plugin Management installation
metadata, and installed package manifests. Only portable names, observed
versions, and installation methods are recorded; no account identifiers,
credentials, user configuration, or runtime implementation caches are included.
`cached-bundle` explicitly denotes cache observation rather than a verified
current installation. Native CLI and connector installation states are recorded
separately because the two inventories do not expose the same surface.

[samber/cc-skills](https://github.com/samber/cc-skills) is included at the user's
installed commit `123cb155f5ab5751fc13c8027fbfa5eb0d3773c6`, plugin version `2.4.0`.
Its 21 skill directories and runtime references/assets are preserved as an
optional native plugin. The MIT notice is retained at
[plugins/cc-skills/LICENSE](plugins/cc-skills/LICENSE), and its source record is
[UPSTREAM.json](plugins/cc-skills/UPSTREAM.json). Repository/CI/publishing setup,
eval suites, and generated artifacts are omitted. The compatibility manifest is
limited to the skill bundle; no hooks or account connections are added.

OpenAI plugins are restored from their official source or supported app runtime
rather than redistributed from private local caches. The four marketplace
selectors were checked against the local official marketplace. Google Contacts
and Sites use the plugin directory/app connection flow because they were not
listed as CLI marketplace entries in this snapshot. Host-managed feature names
do not promise availability in every client, account, or future release.

The new installer mode is tested against a simulated native CLI for argument
boundaries, dry-run, conflicts, idempotence, disabled-state preservation, and
partial failure. Real connector installation or OAuth authorization was not run
as a test. The vendored workflows themselves were not all executed or model-evaluated.

Primary documentation checked during adaptation:

- [Codex skill discovery and authoring](https://learn.chatgpt.com/docs/build-skills)
- [Rust 2024 edition guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)
- [Zig language documentation](https://ziglang.org/documentation/)
- [Swift 6.2 language and concurrency changes](https://www.swift.org/blog/swift-6.2-released/)
- [Text representation and character length](https://github.com/haskell/text/blob/master/src/Data/Text.hs)
- [Criterion evaluation depth](https://github.com/haskell/criterion/blob/master/Criterion/Main.hs)
- [GHC 9.2.8 bundled library versions](https://downloads.haskell.org/ghc/9.2.8/docs/html/users_guide/9.2.8-notes.html)
- [Codex plugin packaging and local marketplaces](https://developers.openai.com/plugins/build/plugins)
- [Codex native CLI reference](https://learn.chatgpt.com/docs/cli/reference)

Documentation examples are conditional reference material. Match them to the
target project's dependency versions and actual toolchain. No claim is made
that every example across all references was built or executed.

The installer and packaging have local automated checks. These do not constitute
a Snyk service scan or end-to-end evaluation of model skill selection.
