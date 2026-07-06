---
title: Getting started
---

Welcome to Hegel! This page will orient first-time Hegel users and direct you to next steps.

Hegel exists because of a problem: writing a good property-based testing library is hard. Writing a good property-based testing library in *every language*? Even more so.

Many of the hardest parts of writing a PBT library can in principle be reused. Bug-finding distributions, automatic shrinking, and flexible generator primitives could all be written once and used in every language. This would lower the barrier to entry and make world-class property-based testing available to all languages in a way which simply wasn't feasible before.

<!-- consolidate the best of property-based testing in every language. -->

Hegel is the realization of this idea.

Hegel is several things. It is a shared native engine ([libhegel](/reference/libhegel), a Rust port of [Hypothesis](https://github.com/hypothesisworks/hypothesis)'s internals) implementing the core of property-based testing once. It is also a family of libraries, one per language, that present an idiomatic property-based testing API on top of that engine.

When we say "Hegel", we might mean any or all of these things. Your interest in Hegel will therefore determine which you might want to read further about:

- Want to *use* Hegel? [hegel-rust](https://github.com/hegeldev/hegel-rust), [hegel-go](https://github.com/hegeldev/hegel-go), [hegel-cpp](https://github.com/hegeldev/hegel-cpp), [hegel-typescript](https://github.com/hegeldev/hegel-typescript), [hegel-java](https://github.com/hegeldev/hegel-java), and [hegel-ocaml](https://github.com/hegeldev/hegel-ocaml) are fully-fledged property-based testing libraries, built on Hegel.
- Want to learn how the pieces fit together — or build Hegel for a new language? See [How Hegel works](/explanation/how-hegel-works), or jump straight to the [libhegel reference](/reference/libhegel).
