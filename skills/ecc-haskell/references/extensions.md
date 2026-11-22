# Language standards, extensions, and deriving

Adapted from mightybyte's extension guidance, without a mandatory house list.

Respect `default-language`, common stanzas, component-specific settings, module
pragmas, and any generated package configuration. Haskell2010, GHC2021, and
GHC2024 select different sets of features; support depends on the actual compiler.
A feature already implied by the chosen language standard need not be repeated
as a pragma. Do not switch standards as a side effect of an unrelated fix.

Use local pragmas for focused features when that fits the project policy, and
shared defaults where the project intentionally standardizes them. No universal
four-extension list defines correctness. `OverloadedStrings`, `TemplateHaskell`,
GADTs, type families, and deriving features have different tradeoffs; select from
the requirement and explain non-obvious effects.

- `OverloadedStrings` changes literal interpretation. Resolve ambiguous types
  deliberately instead of assuming every string literal is `Text`.
- `BangPatterns` forces pattern-bound values only to the required evaluation
  depth; it is not general deep evaluation.
- `ScopedTypeVariables` has explicit-scoping rules. An explicit `forall` may be
  needed to make a signature's type variable scope over an implementation.
- `DerivingStrategies` can clarify whether an instance is stock, newtype,
  anyclass, or via another representation. Check generated behavior, not only syntax.
- `DeriveAnyClass` may create an instance relying on class defaults; it is not
  interchangeable with newtype deriving and can leave required methods missing.
- GADTs/type families can make real invariants expressible. Do not treat their
  presence as a defect or introduce them when a simpler model already works.
- Roles and representation matter when an invariant relies on a phantom type
  or `coerce`; check the exported abstraction, not just the type signature.
- Record extensions affect selectors, disambiguation, and updates. Preserve
  existing public field APIs unless a migration is part of the task.
- Template Haskell has staging/declaration-group constraints and compile-time
  execution effects. Preserve its build dependencies and inspect generated code
  when diagnosing errors; replacing it is not automatically an improvement.

For warnings or inference errors, reproduce under the correct component settings
before adding extensions. An extension can make a program typecheck while hiding
a design ambiguity. Conversely, an advanced feature can be the clearest existing
solution; keep review findings tied to actual correctness/maintainability costs.
