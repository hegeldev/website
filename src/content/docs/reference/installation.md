---
title: Installation reference
---

(TODO lots of stuff to say here, including venvs, HEGEL_SERVER_COMMAND, version pinning, etc)

The [hegel-core](https://github.com/hegeldev/hegel-core) server uses [Hypothesis](https://github.com/hypothesisworks/hypothesis) as the underlying library to provide data generation, shrinking, and so on. Every Hegel library, regardless of language, therefore has an implicit dependency on Python.

:::note
We recognize this is less than ideal for a number of reasons and will make some people unhappy. Sorry! We decided it was the most pragmatic option.

Our current long-term plan is to rewrite Hypothesis in rust and provide per-language bindings, which would eliminate this dependency on Python. We aren't promising this or committing to any timelines, however.
:::

:::note
You may have been directed to this page by an error during the installation of a Hegel library. If that is you, and any part of how we install Hegel or the tradeoffs we made is still confusing after reading this page, *please* [open an issue against hegeldev/website](https://github.com/hegeldev/website/issues/new) so we can improve it for everyone.
:::
