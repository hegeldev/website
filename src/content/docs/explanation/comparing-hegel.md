---
title: Comparing Hegel to other Property-based Testing Libraries
---

Something we've been (quite reasonably) asked is "Why would we use Hegel instead of other property-based testing libraries?"

Part of our answer is: Right now, if you're a happy user of another property-based testing library, you probably shouldn't! Hegel is in its early days, and while we think it's going to long-term be the best property-based testing library in every language it supports, it's currently got an unstable API, likely has a number of rough edges and bugs, and has performance that is at best OK. We're going to fix all of those things, but if you're currently happy with your property-based testing, there's no reason you shouldn't wait for us to do so.

If you're currently an *unhappy* user of another property-based testing library, or not using property-based testing at all, we do think Hegel has a number of distinct advantages over other libraries that mean that it's worth your while to give it a try.

The big advantages that we think are distinctive to the Hegel/Hypothesis model are:

* Hegel has an API style that looks much more like "normal testing", and is built around freely intermixing generation and testing, in a way that makes it much more natural to test highly stateful code and APIs. This is most obvious in our support for stateful testing, in which you generate operations against some stateful system, but is supported everywhere in how you use the library. 
* Hegel gives you a flexible library of generators that you can compose, which gives you much better control over what sorts of data you test with.[^1] You can impose validity constraints at any point, construct the right shape of problem for your tests, etc. As well as making it easier to write tests, this also increases the power of the tests you write because it lets the library know where boundary cases are, and allows it to have a much better exploration of the state.
* Hegel's generation benefits from a lot of the refinements in Hypothesis that allows it to find edge cases that less sophisticated generation strategies will often miss.
* "Internal shrinking" means that you never have to write a shrinker, and that "Could this data have been generated?" is the universal source of truth for whether you can see a particular piece of data. It's common in other property-based testing libraries to have shrinking be a separate process to generation (even when the API bundles shrinkers with generators), so you might commonly e.g. enforce that an integer in your data always be non-zero, find a real bug satisfying that condition, and then have the shrinker replace it with a zero which gives you a spurious failure.
* The shrinker is also just much better than most other property-based testing libraries that try to do similar things. A common pain point is the use of `flat_map` or `bind` - anything where shape of data generated depends on some previously generated data. In most property-based testing libraries this just completely breaks shrinking. In Hegel, it mostly[^2] just works.
* We support *test caching*[^3], which means that if you rerun a failing test it will always fail in the same way. Some other property-based testing libraries do this with seed saving, which is a lot better than nothing, but still requires you to rerun the whole shrinking process, which is a lot slower.
* We support *explicit test cases*^[4], which allow you to permanently enshrine important test cases in your source code, in a way that helps readability and reproducibility.
* We have a *stateful testing API* which is based on Hypothesis's and is much better than almost everyone else's, both in terms of the convenience of its API and because you don't have to do your generation up front and can depend arbitrarily on the current state of the system while generating.

Additionally, if you're running on Antithesis, using Hegel lets the Antithesis fuzzer control your data generation, in a way that will get you much more effective test case generation than you will get in normal property-based testing.

## Hegel vs proptest

In Rust, the closest comparable property-based testing library is proptest. Here are what we think of as the advantages of Hegel over proptest specifically:

* We think the Hegel generator combinator's are a much more usable and flexible design than proptest's generator language. We've also just got a bunch of special-purpose generators for common formats that aren't built into proptest.
* Proptest's shrinking has a number of limitations. It doesn't compose well, and you may be forced to write your own shrinker in order to get good shrinking for your data, which is annoying to do and relatively hard to get right in a way that doesn't hit soundness bugs.
* Explicit test case support is a really nice ergonomic feature missing from proptest.
* Stateful testing in Hegel doesn't have any good proptest equivalent

There are also some ways that proptest is just clearly better at the moment:

* Proptest is currently more stable and mature.
* Proptest has broader integration into the ecosystem. e.g. Hegel does not currently support `cargo fuzz` or integrate with the `arbitrary` crate. We intend for it to do so, but don't currently have a timeline on that.
* Proptest generation likely performs much better in a wide variety of cases^[5] because it's in pure rust.
* Hegel currently has a Python dependency.
* Proptest has `no_std` support, while Hegel requires quite a lot of OS functionality.
* Proptest has `async` support, which Hegel currently lacks.

We intend to fix all these, but right now if any of them are a dealbreaker, you just have to use proptest, no questions.

In contrast the only thing where we think there's a similarly clear cut reason to use Hegel is that if you want something like our stateful testing, you're just going to have a vastly better time using it than proptest.

## Hegel vs Rapid

Honestly, we think Rapid is very solid, and Hegel and Rapid are very similar. Right now, we think you should probably use Rapid unless you specifically want Antithesis support. We think Hegel for Go is going to improve pretty rapidly in the coming months, and you're more than welcome to start using it now on that basis, but if you're already using Rapid then don't switch yet.

## Comparing for yourself

[The Claude Code Hegel skill](https://github.com/hegeldev/hegel-skill) is pretty good at porting tests from other property-based testing libraries and will probably one-shot a port. If you're interested in seeing how your tests would look under Hegel, it might be worth spending an afternoon looking at the actual differences on your own tests - whether they read better, and also whether they find bugs that the original tests wouldn't have.

[^1]: We also support auto-deriving of default generators for most types in Rust, and intend to do this in every language we can manage.
[^2]: Specifically: We have an abstract model of shrinking which allows for it to always work, and a shrinker that can usually navigate that abstract model in common cases. It won't always produce perfect results, but where it doesn't it's just a bug we can improve rathe than a fundamental limitation of the model. Also, because there is a single centralised shrinker, it has *much* more work put into it than most shrinkers people write themselves, so even where it's imperfect it's probably better than most hand-written shrinkers you're likely to use.
[^3]: Called the test database in Hypothesis, but it's really more like a cache than a database - we largely decided not to persist it.
[^4]: At least, we do in Rust right now, and intend to roll it out in other languages but haven't yet.
^[5]: The difference is less stark than we expected though.
