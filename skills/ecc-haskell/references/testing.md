# Behavioral and property testing

Adapted from mightybyte's Hspec/QuickCheck guidance and review checklist.
Use the project's Hspec, Tasty, Hedgehog, QuickCheck, or other established runner.
No one framework is mandatory.

Test the contract: successful behavior, malformed/truncated input, limits,
failure propagation, resource cleanup, and cancellation where relevant. For
numeric newtypes, include zero, negative values, exact maximum, and the first
unrepresentable value. A parser/decoder must not bypass the smart constructor.

Use properties with meaningful laws and valid generators. Roundtrips are useful
but insufficient alone: an encoder and decoder can share the same mistake.
Include known examples or an independent oracle where appropriate. When using
smart constructors, avoid both excessively discarded inputs and a property that
passes vacuously for every invalid generated value. Preserve invariants during
shrinking as well as generation.

For `Domain.Positive`, useful checks include:

- Every accepted input roundtrips through `positiveValue` without narrowing.
- Inputs in `[1, maxBound :: Int]` are accepted.
- Nonpositive and oversized inputs return their documented error cases.
- Reconstructing an accepted value preserves it.

Generate boundary values deliberately. Record the failing seed/counterexample
and keep regressions for actual bugs. A larger random case count alone does not
prove that a failure path was exercised.

## Laziness and observable failures

Evaluating a result to WHNF may leave exceptions hidden in its fields or tail.
Force the depth relevant to the contract before claiming a computation succeeds
or throws. Use `evaluate` with `force` when the assertion requires NF and an
appropriate `NFData` instance exists. Do not accidentally benchmark or test only
the construction of an unevaluated result.

For I/O, use per-test temporary files, controlled services, clocks, and randomness
instead of production resources. Await/join workers before assertions and cleanup.
Use MVars/STM/latches or supported deterministic scheduling tools rather than
sleep-based assumptions. Test cancellation while the real operation is active;
adding a cancellation check only to test code does not test production cleanup.

For asynchronous exceptions, cover the acquisition-to-ownership transition and
cleanup on worker failure. A timeout is a failure bound, not proof that every
interleaving was explored. Do not make a shared mutable fixture safe merely by
serializing one suite if unrelated tests can still access it.

Follow existing coverage and compiler-matrix requirements. For review, identify
specific missing behaviors instead of demanding more tests or a percentage for
every edit. Do not report compilation, runtime tests, property runs, or model
evals as passed when only a structural Markdown check ran.
