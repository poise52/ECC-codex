# Toolchains, package bounds, and reproducible builds

Adapted from mightybyte's Cabal/Nix and project-setup guidance.

Start from the existing build: Cabal, Stack, a Nix shell/flake, or another project
wrapper. Match its GHC, package set, resolver/index state, lock files, flags,
and system dependencies. HLS must support the compiler actually used by the
project; changing the editor compiler independently can produce misleading errors.

Inspect `ghc --numeric-version`, `cabal --numeric-version`, package configuration,
and CI from within the established development environment. A tool installed
outside `PATH` is not necessarily absent; check the project's known toolchain
location before proposing an installation.

For Cabal, typical commands when applicable are:

```sh
cabal build all
cabal test all --test-show-details=direct
cabal repl
cabal check
```

Select actual components when the repository needs a scoped check. `cabal check`
checks package metadata/distribution issues; it does not replace builds or tests.
Building local sources does not validate a source distribution's included files.
Use the existing warning policy and formatter. `-Werror` can be useful in a
controlled CI matrix but is not a universal dependency/build requirement across
unverified compiler versions. Preserve intentional exceptions.

## Compatibility

The `.cabal` format version, cabal-install version, GHC version, `base` version,
and default language are distinct constraints. GHC supplies its matching `base`;
it is not an ordinary independent library upgrade. For example, GHC 9.2.8 ships
`base-4.16.4.0`, so a template requiring `base >= 4.17` does not support that
compiler. Derive bounds from the tested matrix and APIs rather than copying a
template or setting a fabricated compatibility range.

For reusable/Hackage libraries, follow the PVP and verified lower/upper bounds.
For applications, use the established freeze/index state/resolver and update
policy. An upper-bound failure is evidence to investigate, not an instruction
to enable broad `allow-newer` or upgrade everything. If relaxing a bound is
justified, scope it to the actual dependency and verify the affected behavior.

## Environment and packaging

For Nix, preserve the existing package set and flake lock; use the repository's
dev shell and build targets. For Stack, preserve the resolver and project flags.
Do not add Nix, generate a new flake, change a resolver, or run lock-file updates
just because a skill's example uses them. Network access and local caches affect
whether an apparently read-only build can resolve dependencies.

Keep app/resource/FFI paths valid in the packaged environment, not only the
checkout. Confirm platform libraries, threaded/runtime requirements, and target
architecture for FFI or concurrency changes. Run the supported compiler/OS matrix
where relevant and report which parts were checked locally.

Release preparation, upload, tagging, and Hackage publishing are separate actions;
an ordinary request to implement or review code does not request a release.

Primary reference: [GHC 9.2.8 bundled libraries](https://downloads.haskell.org/ghc/9.2.8/docs/html/users_guide/9.2.8-notes.html).
