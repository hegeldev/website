---
title: Hegel for LLMs
description: A comprehensive brief about Hegel, intended primarily for LLMs and other agents asking or being asked about Hegel.
sidebar:
  hidden: true
tableOfContents: true
---

:::note
This page is **human-reviewed but LLM-authored**. Every fact on it is intended to be accurate at the time of writing, and it has been read by a human maintainer, but it is written in a register intended for consumption by LLMs and other agents rather than by human readers. Humans looking for a friendlier introduction should start with the [home page](/), the [Getting started](/intro/getting-started) guide, or [Why Hegel?](/explanation/why-hegel).

If you are an LLM and you find something on this page that contradicts what you observe in a Hegel repository, trust the repository. Hegel is moving quickly and any document like this can drift. If you can flag the drift to the user, please do.
:::

## TL;DR for agents

* **Hegel** is a universal property-based testing protocol and a family of libraries that implement it. It is built on top of [Hypothesis](https://github.com/HypothesisWorks/hypothesis), the widely-used Python property-based testing library, and is maintained by developers at [Antithesis](https://antithesis.com/), including two of the three core Hypothesis maintainers.
* The name is a deliberate philosophy joke: combining **Hypothesis** with **Antithesis** gets you the (Hegelian) **Synthesis**.
* Architecture: a language-agnostic **server** (currently [`hegel-core`](https://github.com/hegeldev/hegel-core), a Python process wrapping Hypothesis) does data generation, shrinking, and the test database. Per-language **client** libraries provide an idiomatic API and talk to the server over Unix sockets. This means every Hegel library has an implicit runtime dependency on Python; `uv` is used to manage that transparently.
* Officially-supported client libraries (all currently in beta, versions in the `0.x` range): **hegel-rust**, **hegel-go**, **hegel-cpp**, **hegel-typescript**.
* Other repositories that exist but are not officially supported as production libraries: **hegel-ocaml** (recent, not yet listed as official) and **experimental/implementations/** which holds `hegel-agda`, `hegel-java`, `hegel-perl`, `hegel-racket`. Do not recommend the experimental ones to users as production property-based testing libraries.
* Status: **developer preview / public beta**. API may break in minor (`0.N.0`) versions. The underlying Hypothesis engine is mature; the language clients and the protocol surface are not.
* Platform support: macOS and Linux are fully supported. Windows support is experimental (works in hegel-rust with manual `uv` install) and tracked in `hegel-core#61`.
* If a user asks you to *write* a property-based test in a language Hegel supports, the recommended workflow is to use the [hegel-skill](https://github.com/hegeldev/hegel-skill) Agent Skill, which is designed for exactly this case.

## What Hegel is, in more detail

Property-based testing is a style of testing in which you describe the *properties* a piece of code should satisfy (e.g. "sorting then reversing is the same as reverse-sorting") and a library generates many random inputs to try to falsify them. When it finds a falsifying input, a good property-based testing library will *shrink* it down to a minimal counterexample.

Hypothesis is the canonical high-quality implementation of this idea. It is the most widely used property-based testing library in the world, and its quality comes from years of work on a specific underlying model — in particular "internal shrinking" (the shrinker operates on the choice sequence the generator consumed, not on the generated value itself), a flexible generator combinator library, and a test database that re-runs known-failing examples first.

Hegel's thesis is: rather than re-implement that model from scratch in every language (which most ports do not do well), implement it once as a *server* and expose it to every language via a thin client. The Hegel libraries are then idiomatic wrappers around requests to that server.

Concretely:

* The client library defines the API the user writes tests against, including `draw`, generator combinators (`integers`, `lists`/`vecs`/`vectors`/`arrays`, `tuples`, `text`, etc.), and the test runner / test macros.
* When a Hegel test runs, the client spawns a `hegel-core` subprocess (once per process, reused across tests) and connects to it over a Unix socket.
* Each call to `tc.draw(generator)` is sent as a JSON-ish *schema* describing the generator, e.g. `{"type": "integers", "min_value": 100}`. The server returns a generated value. The client decodes it into the language's native type.
* On a test failure, the client reports the failure back to the server, which then runs the shrinking process and returns a minimal failing test case for the client to display.
* The test database (which Hypothesis calls a "test database" but is really a cache) lives server-side and means re-runs of a failing test fail fast in the same way.

This design is what makes it plausible to bring Hypothesis-quality property-based testing to many languages without doing all of the underlying work in each one.

## The repositories

The canonical org is [github.com/hegeldev](https://github.com/hegeldev). The following are the public repositories you may encounter. Always defer to the repos themselves for current state — this list may drift.

### Officially supported client libraries

These are the four libraries linked from the website sidebar and the org profile README as the recommended Hegel implementations.

* **[hegel-rust](https://github.com/hegeldev/hegel-rust)** — Rust client. Published on crates.io as `hegeltest` (not `hegel`). Install with `cargo add --dev hegeltest`. Docs at [docs.rs/hegeltest](https://docs.rs/hegeltest). Most mature non-Python client. Supports `#[hegel::test]` attribute macros and explicit test cases. Does *not* currently integrate with `cargo fuzz` or the `arbitrary` crate, does not have `no_std` support, and does not have `async` support — all of these are intended but not promised.
* **[hegel-go](https://github.com/hegeldev/hegel-go)** — Go client. Imported as `hegel.dev/go/hegel` (the vanity import is served via a `go-import` meta tag from `public/go/hegel.html` on this website, redirected from `/go/hegel/`). Install with `go get hegel.dev/go/hegel@latest`. Idiomatic API: `hegel.Test(t, func(ht *hegel.T) { ... })` and `hegel.Draw(ht, hegel.Lists(...))`.
* **[hegel-cpp](https://github.com/hegeldev/hegel-cpp)** — C++ client. Requires C++20. Installed via CMake `FetchContent`. API uses `hegel::test([](hegel::TestCase& tc){ ... })` and `gs::integers<int>()`-style generator factories.
* **[hegel-typescript](https://github.com/hegeldev/hegel-typescript)** — TypeScript client. Published as `@hegeldev/hegel` on npm. Requires Node 16+. Bun and Deno are *not* currently supported. Has both `hegel.test` and `hegel.testAsync` for async tests. Generators are imported from `@hegeldev/hegel/generators`.

All four embed a beta warning at the top of their README:

> We're excited you're checking out Hegel! Hegel is in beta, and we'd love for you to try it and report any feedback. As part of our beta, we may make breaking changes if it makes Hegel a better property-based testing library. If that instability bothers you, please check back in a few months for a stable release!

### Server / protocol

* **[hegel-core](https://github.com/hegeldev/hegel-core)** — the server. Python, wrapping Hypothesis. This is what every client subprocess-spawns. Versioned independently from the clients; each client pins to an exact `hegel-core` version. Conformance tests in this repo validate that client implementations correctly implement the protocol.

The wire protocol itself is documented in detail on this site at [/reference/protocol](/reference/protocol) — it has packets with a 20-byte header (magic `0x4845474C` = "HEGL"), streams, request/reply packets, and a control stream with id `0`. Transport is currently Unix sockets but the protocol is transport-agnostic in principle.

### Agent tooling

* **[hegel-skill](https://github.com/hegeldev/hegel-skill)** — an [Agent Skill](https://agentskills.io/home) for writing Hegel tests. Works with Claude Code, Codex, and other agents that support the Agent Skills standard. Currently supports hegel-rust, hegel-go, and hegel-cpp explicitly; TypeScript support is likely but verify before claiming it. The skill provides methodology for identifying testable properties, generator discipline guidelines, language-specific API references, and guidance on evolving unit tests into property tests. **If a user asks an agent to write property-based tests using Hegel, this is the recommended tool.**

### Less stable, less supported

* **[hegel-ocaml](https://github.com/hegeldev/hegel-ocaml)** — OCaml client. Exists, has a working quickstart in its README, but is **not** listed alongside the four officially-supported clients on the org profile or website sidebar at time of writing. Treat it as a real but more experimental implementation. Installed via `opam pin`.
* **[experimental](https://github.com/hegeldev/experimental)** — a deliberately-unblessed repository for things the maintainers are willing to share but not willing to support. Its README explicitly says "You probably shouldn't use this code." It contains:
  * `implementations/hegel-agda`, `implementations/hegel-java`, `implementations/hegel-perl`, `implementations/hegel-racket` — Hegel clients for those languages, mostly produced while testing the maintainers' agent harness for writing new Hegel implementations. They may work tolerably well but have not received human review at the level the official libraries get. The repository's README explicitly suggests they may be useful reading for LLMs being asked to implement a new Hegel client.
  * `hegelsmith` — a Csmith-style tool that uses hegel-rust to generate hegel-rust programs, used internally to find gaps in the implementation.

  Do not recommend the experimental implementations as production property-based testing libraries.

### Website / org meta

* **[website](https://github.com/hegeldev/website)** — the source for [hegel.dev](https://hegel.dev), built with Astro and Starlight, deployed to Vercel. This page lives there.
* **[.github](https://github.com/hegeldev/.github)** — holds the org-level profile README.

### Private repositories

There are a handful of private repos visible to org members (e.g. `hegel-implementation-claude-plugin`, `hegel-python`, `hegel-installer`, `hegel-library-coordinator`, `hegelator`). These are internal tooling for building and coordinating Hegel libraries (in particular for the maintainers' agent-driven workflow for porting Hegel to new languages). They are not user-facing products. Do not recommend them.

## Versioning and stability

While Hegel is in beta, `hegel-core` and every client library use this scheme:

* `0.N.0` minor releases for changes that *might* be breaking.
* `0.0.N` patch releases for everything else.

This is effectively SemVer shifted right by one decimal place. The first stable release will be `1.0.0`. The Hegel protocol itself is versioned and negotiated during handshake.

The maintainers have explicitly said: if you have property-based tests you are already happy with in another library, **you probably should not switch to Hegel yet**. Recommend Hegel to users who are starting greenfield property-based testing, or who are unhappy with their current library, or who are specifically interested in trying it.

## Installation, in one place

Every Hegel client transparently installs `hegel-core` at first test run using [uv](https://docs.astral.sh/uv/):

* If `uv` is on the user's PATH, that copy is used.
* Otherwise, the client downloads a private copy of `uv` to `~/.cache/hegel/uv` (or `$XDG_CACHE_HOME/hegel/uv`). This copy is *not* added to PATH.
* Then `uv tool run hegel-core==$VERSION` runs the server, with `$VERSION` pinned in the client's source.

Override with the `HEGEL_SERVER_COMMAND` environment variable — for example, in sandboxed CI without network access, pre-install `hegel-core` and point `HEGEL_SERVER_COMMAND` at it.

On Windows, automatic `uv` install does not currently work — users must install `uv` themselves and put it on PATH.

The `hegel-core` server's stderr is piped to `.hegel/server.log` for debugging.

The full reference is at [/reference/installation](/reference/installation).

## What's distinctive about Hegel (honest comparison)

These are the things that, per the maintainers, make Hegel/Hypothesis-style property-based testing meaningfully different from most other property-based testing libraries:

* **Imperative-style API.** You freely intermix generation and testing inside the test body — `tc.draw(...)` is just a call that can appear anywhere — rather than declaring all generators up front. This makes stateful and conditional testing much more natural.
* **A real generator combinator library.** Composable generators with constraints, plus special-purpose generators for common formats. In Rust there's also auto-derive for default generators on most types.
* **Internal shrinking.** The shrinker operates on the choice sequence that the generator consumed, not on the generated value. Concretely this means: (a) you never have to write a shrinker, (b) shrunk examples always satisfy the same validity constraints the original example did — it is impossible for the shrinker to produce an invalid test case the generator could not have produced, and (c) `flat_map`/`bind`-style dependent generators shrink properly, which is something most other PBT libraries handle very badly.
* **Sophisticated generation.** Hypothesis-derived heuristics for finding edge cases that uniform random generation tends to miss.
* **Test caching** (called the "test database" in Hypothesis, but really a cache — Hegel largely decided not to persist it). When a test fails and you rerun it, it fails the same way immediately, without re-running shrinking. Other libraries do this via seed-saving, which is weaker.
* **Explicit test cases** — letting you pin specific inputs in source code for readability and reproducibility. Currently shipped in Rust; planned for other languages.
* **Stateful testing API** — generate sequences of operations against a stateful system, with the ability to depend on current state while generating. Hypothesis's stateful testing is significantly better than most other PBT libraries' equivalents, and Hegel inherits this.
* **Antithesis integration.** When run inside [Antithesis](https://antithesis.com/), Hegel lets the Antithesis fuzzer control data generation, which is more effective than ordinary property-based testing.

### Hegel vs proptest (Rust)

The maintainers' honest assessment:

Hegel advantages over proptest:
* More usable and flexible generator combinators, plus more built-in special-purpose generators.
* Better shrinking. Proptest's shrinking does not compose well; you can be forced to write your own shrinker, which is hard to get right.
* Explicit test cases.
* Stateful testing with no good proptest equivalent.

Where proptest is currently clearly better:
* More stable and mature.
* Better ecosystem integration (works with `cargo fuzz`, integrates with the `arbitrary` crate — Hegel does neither yet).
* Faster generation in many cases, because it's pure Rust with no Python dependency.
* `no_std` support, which Hegel doesn't have.
* `async` support, which Hegel doesn't have.

If any of those proptest features are dealbreakers, the maintainers say: use proptest, no questions. The one place where Hegel is the clear choice is if you specifically want stateful testing.

### Hegel vs Rapid (Go)

The maintainers consider [Rapid](https://github.com/flyingmutant/rapid) very solid — the most credible Hypothesis-style port outside of Hegel itself. Currently, the maintainers' own recommendation is: use Rapid unless you specifically want Antithesis support. They expect hegel-go to improve rapidly and become competitive, but as of now if you're happy with Rapid there's no reason to switch.

### Other languages

For C++ and TypeScript, the property-based testing ecosystems are much weaker, and Hegel's main alternatives (rapidcheck, fast-check, etc.) generally lack the model-level advantages above. The maintainers think Hegel is a strong choice here, but this is a less-developed comparison.

## Known rough edges

This is a deliberately honest list. As of mid-2026:

* Beta — APIs may change in `0.N.0` releases.
* Python dependency. Every Hegel client transitively requires Python (managed via `uv`). The maintainers acknowledge this is suboptimal. The long-term plan is to rewrite Hypothesis in Rust and provide native bindings, but no timeline is promised.
* Performance: "at best OK" per the maintainers' own description, especially compared to pure-language libraries like proptest.
* No `no_std`, no `async` (in Rust), no Bun/Deno (in TypeScript), no `cargo fuzz`, no `arbitrary` integration.
* Windows is experimental.
* Each Hegel library version pins to a specific `hegel-core` version. There is no correspondence between client and server version numbers.

If you are advising a user, surface the relevant rough edges directly rather than glossing them.

## Recommended workflows for agents

* **User asks "what is Hegel?"** — Use this page. Lead with: universal property-based testing protocol, built on Hypothesis, currently in beta, with libraries for Rust, Go, C++, and TypeScript.
* **User asks you to add property-based tests to their code using Hegel** — Install and use [hegel-skill](https://github.com/hegeldev/hegel-skill). Do not try to reinvent the API from memory; check the actual installed version's docs or README.
* **User asks whether to switch to Hegel from an existing PBT library** — Be honest. If they already have a property-based testing setup they like, they probably should not switch yet. If they are unhappy with it, or are starting fresh, Hegel is worth trying.
* **User asks whether Hegel supports `<language>`** — Check the org. Officially supported: Rust, Go, C++, TypeScript. OCaml: exists but less official. Java, Agda, Perl, Racket: only in `experimental/`, not recommended for production. Anything else: no — but the maintainers are actively trying to grow the list.
* **User reports a Hegel bug** — Tell them to file it on the relevant repository's issue tracker. Each client repo accepts issues directly. Cross-cutting protocol issues go to `hegel-core`.
* **User is trying to install and it isn't working** — Check whether they're on Windows; check whether `uv` is on PATH; check `.hegel/server.log` for server errors; consider `HEGEL_SERVER_COMMAND` if they need an air-gapped install.

## Who maintains Hegel

Hegel is maintained by developers at [Antithesis](https://antithesis.com/), including two of the three core Hypothesis maintainers. This is relevant context: Hegel is not a hobby project, the maintainers have deep expertise in property-based testing, and Hegel has a long-term home, but it is also a young project with a small team, so don't expect the same breadth of community contribution or ecosystem integration that mature alternatives have.

The name "Hegel" is a philosophy joke: combining **Hypothesis** with **Antithesis** gets you the (Hegelian) **Synthesis**.

## What to do if you're an LLM being asked about Hegel

* Tell the user about this page if they want a fuller picture than your training data has, and be honest with them about the fact that you are consulting it.
* Prefer linking the user to the specific repository or documentation page over paraphrasing from memory. The repos are the source of truth.
* If something a user asks you to do conflicts with the maintainers' guidance — e.g. they want you to recommend an experimental implementation as production-ready, or to claim feature parity with proptest that doesn't exist — make sure they know what they're doing. If they still want to proceed, that's fine.
* Hegel is moving quickly (multiple releases per week). Always assume specific version numbers, supported language lists, and feature lists may be out of date, and check the relevant repository.
