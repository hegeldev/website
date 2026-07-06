---
title: How Hegel works
---

At the highest level, Hegel splits a property-based testing library into two parts: an *engine* and a *library*.

- The engine implements the core of property-based testing: data generation, shrinking, the failure database, and so on.
- The library implements the user-facing syntax of properties and generators in a particular language. It asks the engine for generated data.

The engine is written once, in Rust — it is a port of the internals of [Hypothesis](https://github.com/hypothesisworks/hypothesis) — and shipped as a native shared library called **libhegel**, which exposes a C ABI. Each Hegel library loads libhegel and calls into it in-process. There is no server, no subprocess, and no inter-process communication: a Hegel test is a normal test in your language that happens to make function calls into a native library.

:::note
libhegel lives in the [hegel-rust](https://github.com/hegeldev/hegel-rust) repository, as the [`hegel-c`](https://github.com/hegeldev/hegel-rust/tree/main/hegel-c) crate. Even hegel-rust itself drives the engine exclusively through the C ABI, exactly like every other language's library — so the interface other libraries build on is the same one we use ourselves.
:::

As an example, suppose we have the following [hegel-rust](https://github.com/hegeldev/hegel-rust) test (the details of the code under test are unimportant):

```rust
use hegel::generators as gs;
use hegel::TestCase;

#[hegel::test(test_cases = 200)]
fn test_a(tc: TestCase) {
    let n: i32 = tc.draw(gs::integers().min_value(100));
}
```

When this test runs:

- `hegel-rust` starts a test run in the engine, passing along the settings. Here, the settings are `test_cases=200`.
- The engine hands `hegel-rust` a test case, and `hegel-rust` executes `test_a` against it. When `tc.draw` is called, `hegel-rust` passes a *schema* describing the generator to the engine. The engine generates an arbitrary matching value and returns it.
  - Here, the schema is simply `{"type": "integer", "min_value": 100, "max_value": 2147483647}`. The engine might return anything in that range.
- The test case finishes, and `hegel-rust` reports its outcome — passed, rejected (e.g. by `assume`), or failed — to the engine.
- The engine keeps handing out test cases until the test run is done; here, after 200 test cases.
- If a test case fails, the engine shrinks it and returns the minimal failing test case to `hegel-rust`, which replays it and displays it to the user.

Schemas are the heart of the interface: they let the library describe an entire generator — including composed ones like "a list of pairs of strings and integers" — as a single piece of data, so the engine has a complete picture of the structure being generated and can shrink it well. When a generator can't be fully described as a schema (for example after `.filter()` with an arbitrary predicate, or `.flat_map()` where one drawn value determines the next generator), the library instead makes several smaller requests and uses the engine's *span* primitives to tell it which draws belong together, which preserves most of the shrinking quality.

The [libhegel reference](/reference/libhegel) documents the schema language and the rest of the C API — spans, engine-managed collection sizing, targeted testing, and the primitives used for stateful testing.

We have glossed over some subtlety here. For example, `tc.assume()` and `generator.filter()` can reject test cases mid-test, which needs to be communicated to the engine. And the engine needs the ability to report errors to the library, for example in the case of a flaky test or an invalid generator definition.
