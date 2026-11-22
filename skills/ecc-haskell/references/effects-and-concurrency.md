# Effects, resources, and concurrency

Adapted from mightybyte's ReaderT, transformer, STM, and concurrency guidance.

`ReaderT Env IO` is a practical application pattern when shared resources and
configuration fit one environment. Explicit parameters, capability classes,
transformers, or effect libraries can be better in another module. Prefer the
existing design unless a concrete requirement exposes a problem.

`StateT` models threaded state, while `IORef`/`TVar` model mutable references.
Replacing one with another can change visibility, lifetime, concurrency,
rollback expectations, and testability. `IORef` is not a transactional or
multi-operation synchronization mechanism. A capability abstraction should
clarify dependencies rather than add boilerplate without a need.

Transformer order changes observable results. This complete example shows
that a typed error can discard the returned state or retain it:

```haskell
module EffectOrder (discardedState, retainedState) where

import Control.Monad.Trans.Class (lift)
import Control.Monad.Trans.Except (ExceptT, runExceptT, throwE)
import Control.Monad.Trans.State.Strict (State, StateT, put, runState, runStateT)

discardedState :: Either String ((), Int)
discardedState = runStateT operation 0
  where
    operation :: StateT Int (Either String) ()
    operation = put 1 >> lift (Left "failed")

retainedState :: (Either String (), Int)
retainedState = runState (runExceptT operation) 0
  where
    operation :: ExceptT String (State Int) ()
    operation = lift (put 1) >> throwE "failed"
```

Discarding a state result does not roll back external I/O performed underneath
the transformer. Replacing `ExceptT` with exceptions also changes how callers
observe and recover from failures; it is not an automatic simplification.

## Resource and exception boundaries

Use `bracket`, `finally`, or the project's resource abstraction to pair
acquisition and release, including exceptional exit. Force lazy results that
depend on a handle inside the resource scope, or stream while the resource is
open. Do not let unevaluated file reads escape a closed handle.

Mask asynchronous exceptions only around the small acquisition/ownership
transitions that require it; restore interruptibility for the actual work.
Broad `try`/`catch` over `SomeException` can turn cancellation into a domain
error or cause a worker to continue indefinitely. Catch the intended exception
types or deliberately rethrow asynchronous cancellation. Cleanup boundaries can
legitimately observe all exceptions when they preserve their propagation.

## Shared state and workers

STM coordinates transactions across TVars; use `retry` and `orElse` for the
actual waiting/alternative contract. Keep nontransactional I/O outside STM;
transactions can retry. A strict TVar update forces the new value only as far
as that operation promises, not necessarily to normal form.

This complete counter uses arbitrary-precision values and an atomic update:

```haskell
module Counter (Counter, newCounter, increment, readCounter) where

import Control.Concurrent.STM
  ( TVar, atomically, modifyTVar', newTVarIO, readTVarIO )

newtype Counter = Counter (TVar Integer)

newCounter :: IO Counter
newCounter = Counter <$> newTVarIO 0

increment :: Counter -> IO ()
increment (Counter value) = atomically (modifyTVar' value (+ 1))

readCounter :: Counter -> IO Integer
readCounter (Counter value) = readTVarIO value
```

For work owned by a caller, use the established structured `async` patterns
such as `withAsync`/`concurrently` where that dependency exists. Define exception
propagation, cancellation, and joining explicitly. Bare `forkIO` or separately
created `async` handles need an owner and cleanup on every exit path. Bound
worker counts and queues; spawning once for every input is not backpressure.
