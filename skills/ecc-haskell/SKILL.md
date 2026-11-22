---
name: ecc-haskell
description: Implement, debug, test, profile, and review Haskell code, including domain types, effects, concurrency, Cabal or Nix builds, and lazy evaluation.
---

# Haskell development and review

Adapted from mightybyte's Haskell coder/reviewer guides. Use the target project's
toolchain, architecture, formatter, and conventions rather than imposing the
source author's house style.

Read project instructions, `.cabal`/`package.yaml`, `cabal.project`, Stack/Nix
configuration, CI, and the actual GHC/library versions. Preserve language
standards, extension policy, bounds, and dependency pins. Do not fix a build by
blindly upgrading GHC, adding `allow-newer`, or introducing a new build system.

Design around actual invariants and failure contracts. Use ADTs, newtypes, smart
constructors, and pure boundaries where they improve correctness. Keep resource
lifetimes, cancellation, shared-state ownership, and evaluation depth explicit.
Haskell's type checker does not prove termination, totality, race freedom, or
the truth of arbitrary domain invariants.

Read only the references relevant to the task:

- For domain models, validated constructors, record APIs, or error types, read
  [types and errors](references/types-and-errors.md).
- For ReaderT/transformer choices, resource cleanup, STM, worker ownership,
  or asynchronous exceptions, read [effects and concurrency](references/effects-and-concurrency.md).
- For unit/property tests, generators, failure paths, or concurrency tests,
  read [testing](references/testing.md).
- For space leaks, strictness, Text/ByteString representation, profiling,
  or benchmark evaluation depth, read [performance](references/performance.md).
- For Cabal/Stack/Nix, package bounds, HLS, builds, or CI, read
  [build and tooling](references/build-and-tooling.md).
- For language standards, deriving, roles, or extension diagnostics, read
  [extensions](references/extensions.md).

When reviewing, prioritize concrete incorrect behavior, partiality, resource
leaks, asynchronous-exception handling, and measured performance problems.
Show the trigger, affected code, and a bounded fix. Distinguish an actual defect
from a design tradeoff or style preference. Existing `ExceptT`, `StateT`, typed
errors, explicit imports, record naming, or lazy data are not findings merely
because another pattern is available. Preserve formatter output.

Run the project's relevant build, tests, warnings, and supported compiler matrix.
Typical Cabal checks are `cabal build all` and
`cabal test all --test-show-details=direct`; use the established environment and
targets. Report unavailable tools and untested variants accurately. Do not run
publishing, skill self-modification, or upstream contribution workflows merely
because the original repository describes them.
