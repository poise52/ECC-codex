# Domain types, records, and failure contracts

Adapted from mightybyte's type-driven development and review guidance.

Use sum types for alternatives, newtypes for identifiers/units, and smart
constructors for validated values. Keep constructors hidden where callers must
not bypass validation. Audit decoding, `Read`, generic construction, and other
exported instances as alternative construction paths. A newtype changes type
identity; it does not validate its contents by itself.

This complete Haskell2010 module provides a positive machine-sized integer
without silently narrowing an arbitrary `Integer`:

```haskell
module Domain.Positive
  ( Positive
  , PositiveError(..)
  , mkPositive
  , positiveValue
  ) where

newtype Positive = Positive Int
  deriving (Eq, Ord, Show)

data PositiveError = NotPositive | TooLarge
  deriving (Eq, Show)

mkPositive :: Integer -> Either PositiveError Positive
mkPositive value
  | value <= 0 = Left NotPositive
  | value > toInteger (maxBound :: Int) = Left TooLarge
  | otherwise = Right (Positive (fromInteger value))

positiveValue :: Positive -> Int
positiveValue (Positive value) = value
```

Named record construction helps when positional arguments are easily swapped.
Keep the existing field naming/access convention; `_type_field`, lenses,
record-dot access, and explicit selectors are alternatives, not universal rules.
Do not introduce `data-default` just because a record occurs at several call
sites. Defaults must be meaningful; required values should remain required.

Phantom types can express state transitions, but a phantom role can also permit
`coerce` between states. If a transition is an invariant, inspect constructor
visibility and roles, using nominal roles where necessary. GADTs and type
families can be appropriate when they encode requirements the simpler model
cannot express. Do not reject them solely because they are advanced.

## Errors

Choose error representation from its consumers and API stability needs:

- A local error only displayed once can be a textual diagnostic.
- A typed error can support recovery, tests, stable public APIs, localization,
  machine-readable telemetry, or future evolution even if one caller only logs it.
- Keep recoverable domain failures distinct from unrelated I/O/runtime failures.
- `Either`, `ExceptT`, exceptions, and validation accumulators have different
  contracts; preserve the established boundary unless the task requires a change.

For public errors, preserve useful structured context and error causes without
logging secrets. Avoid `error`, `undefined`, unchecked indexing, partial patterns,
and forced `fromJust` in reachable production paths unless the invariant is
actually established and the chosen failure behavior is part of the contract.
Pattern matching or `NonEmpty` often makes that proof clearer.

An email example that merely checks for `@` is not full address validation.
Use examples as domain-specific contracts, not as evidence that every real-world
format has been validated.
