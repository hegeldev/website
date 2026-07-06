---
title: Installation reference
---

:::note
You may have been directed to this page by an error during the installation of a Hegel library. If that is you, and any part of how we install Hegel or the tradeoffs we made is still confusing or misleading after reading this page, *please* [open an issue against hegeldev/website](https://github.com/hegeldev/website/issues/new) so we can improve it for everyone.
:::

Every Hegel library is built on **libhegel**, a native shared library (`libhegel.so`, `libhegel.dylib`, or `libhegel.dll`) containing Hegel's data-generation and shrinking engine. The engine is a Rust port of [Hypothesis](https://github.com/hypothesisworks/hypothesis)'s internals; each language library calls into it in-process through its C ABI. There is no server, no subprocess, and no Python dependency.

Prebuilt libhegel binaries are published as assets on [hegel-rust releases](https://github.com/hegeldev/hegel-rust/releases), named `libhegel-<os>-<arch>.<ext>` with a `.sha256` checksum sidecar, for Linux (amd64/arm64), macOS (Apple Silicon), and Windows (amd64/arm64). See the [libhegel reference](/reference/libhegel) for details.

Each library pins the exact libhegel version it was built and tested against, and verifies downloaded binaries against checksums baked into its own source, so you never need to (and shouldn't) pick a libhegel version yourself.

How the pinned libhegel gets onto your machine varies by library:

## hegel-rust

Nothing to install: the engine is a Rust crate, compiled into your test binary like any other dependency. `cargo add --dev hegeltest` is all you need.

## hegel-go

`hegel-go` loads libhegel at runtime using pure-Go dynamic loading — no cgo, so no C toolchain is needed and `CGO_ENABLED` is irrelevant. The library is located as follows:

- If the `HEGEL_LIBHEGEL_PATH` environment variable is set, that library is loaded directly, with no fallback.
- Otherwise, the pinned version is downloaded from the hegel-rust GitHub release, verified against a SHA-256 checksum compiled into hegel-go, and cached in `~/.cache/hegel-go/libhegel/<version>/` (via your OS's user cache directory). Subsequent runs reuse the cached copy until the pinned version changes.

Setting `HEGEL_LIBHEGEL_NO_DOWNLOAD=1` disables the downloader entirely, which is useful to guarantee sandboxed test environments never touch the network — combine it with `HEGEL_LIBHEGEL_PATH` pointing at a library you provisioned yourself.

## hegel-typescript

The npm package bundles libhegel for every supported platform — `npm install --save-dev @hegeldev/hegel` gets you everything, works offline, and runs no install scripts. At runtime the bundled library for your platform is loaded via FFI, or, if `HEGEL_LIBHEGEL_PATH` is set, that library is used instead.

Hegel for TypeScript requires Node 20.11+. Bun and Deno are not currently supported.

## hegel-java

The jar bundles libhegel for Linux (amd64/arm64) and macOS (Apple Silicon), and binds it with the Java Foreign Function & Memory API (no JNI), which is why Java 22+ is required. At runtime the library is resolved in this order:

- `HEGEL_LIBHEGEL_PATH`, if set.
- The OS shared-library search path (`LD_LIBRARY_PATH` on Linux, `DYLD_LIBRARY_PATH` on macOS).
- The jar-bundled library, unpacked to `~/.cache/hegel-java/libhegel/<sha256>/` (or under `$XDG_CACHE_HOME` if set) and reused from there.

You'll also want to pass `--enable-native-access=ALL-UNNAMED` to the JVM running your tests to silence the FFM native-access warning.

## hegel-cpp

CMake downloads the pinned prebuilt libhegel for your platform at configure time and verifies it against its published SHA-256 checksum; your targets then link `hegel`, which takes care of the rest. To use a locally built engine instead — for example on a platform without a prebuilt binary — pass `-DHEGEL_LIBHEGEL_LIBRARY=/path/to/libhegel.<ext>`, which skips the download entirely.

## hegel-ocaml

The opam package bundles the prebuilt libhegel matching your platform. At runtime the library is resolved in this order:

- `HEGEL_LIBHEGEL_PATH`, if set (either the library file itself or a directory containing it).
- The copy bundled with the opam package.
- A sibling `../hegel-rust` checkout's `target/release` or `target/debug` build (for Hegel development).
- A SHA-256-verified download from the hegel-rust GitHub release, cached in `~/.cache/hegel-ocaml/libhegel/<version>/` (or under `$XDG_CACHE_HOME` if set).

Setting `HEGEL_LIBHEGEL_NO_DOWNLOAD=1` disables the download fallback.

## Building libhegel yourself

If you are on a platform without a prebuilt binary (for example Intel macOS), or you want full control over the binary you run, build libhegel from source: check out [hegel-rust](https://github.com/hegeldev/hegel-rust) and run `cargo build --release -p hegeltest-c`. This produces `target/release/libhegel.<ext>`, which you can hand to your library via `HEGEL_LIBHEGEL_PATH` (or `-DHEGEL_LIBHEGEL_LIBRARY` for hegel-cpp).

Note that each library expects the specific libhegel version it pins, and will warn or error on a mismatch, so build from the corresponding hegel-rust release tag.

## Troubleshooting

This process should ideally be transparent to you. If it breaks without giving a very clear error message about what you need to do to fix it, that's a bug and we'd appreciate it if you reported it, along with any information you can give us about the environment that triggered the problem.
