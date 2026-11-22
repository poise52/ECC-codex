# Evaluation depth, representation, and measurement

Adapted and corrected from mightybyte's performance guidance.

## WHNF is not NF

`seq`, bang patterns, strict fields, `foldl'`, and strict-state operations do not
universally evaluate nested values to normal form. For example, forcing the
outer `Just` or list constructor does not force its payload or tail. Even a
strict fold can retain thunks inside a tuple/record accumulator. Inspect the
actual accumulator structure and use strict fields or deeper evaluation only
where the required semantics and measurements justify it.

This complete module exposes the distinction for list results:

```haskell
module Evaluation (toWHNF, toNF, sumStrict) where

import Control.DeepSeq (deepseq)
import qualified Data.List as List

toWHNF :: [Int] -> ()
toWHNF values = values `seq` ()

toNF :: [Int] -> ()
toNF values = values `deepseq` ()

sumStrict :: [Integer] -> Integer
sumStrict = List.foldl' (+) 0
```

Laziness supports streaming, short-circuiting, recursive structures, and avoiding
unused work. Blanket strict fields or replacing every fold is not a proof of
correctness or speed and can change termination behavior. Profile a real space
leak before changing evaluation throughout a codebase.

## Text and collection representation

Modern `text` 2.x uses UTF-8 internally. `Data.Text.length` counts characters
in O(n); internal byte length is not character count. Older `text` versions used
another representation, so inspect the installed version before low-level claims.
`String` is a character list: some operations, such as accessing its outer
constructor, are O(1), while traversing/counting is O(n). Choose `Text`, bytes,
lists, vectors, maps, and sets for their actual semantics and workload; `String`
at a small existing API boundary is not automatically a performance defect.

Strict reads keep complete bounded data in memory. Lazy bytes/text can be useful
but do not by themselves provide bounded memory, exception safety, or a sound
resource lifetime. For large inputs use a streaming API with explicit resource
ownership and measure retained memory.

## Benchmark the result consumed by the application

With Criterion, `whnf` evaluates the result only to WHNF. For the complete output
of `map` or a full sorted list, `nf` is usually the relevant harness; `whnf` can
measure only the first exposed constructor or a partially demanded result.
WHNF is appropriate when that is the actual demand, or for scalar results such
as `Int` whose WHNF already captures the relevant computation.
`nfIO`/`whnfIO` similarly differ in result evaluation depth.

Force inputs and arrange fixtures outside the timed region when setup is not
part of the operation. Avoid sharing a memoized result between repetitions, and
separate steady-state behavior from cold caches. Keep build optimization, GHC,
RTS settings, hardware, input shape, and correctness checks comparable.

Use cost centers, heap/eventlog profiling, RTS statistics, and tools already
supported by the build to locate retained thunks, allocation, GC pressure,
contention, or I/O. Profiling builds and libraries may need explicit support;
do not assume a binary exists at `./package-name` or that profiling flags work
on an ordinary release binary. Use `cabal list-bin`/the project's runner.

Primary references: [Text implementation](https://github.com/haskell/text/blob/master/src/Data/Text.hs),
[Criterion evaluation harness](https://github.com/haskell/criterion/blob/master/Criterion/Main.hs).
