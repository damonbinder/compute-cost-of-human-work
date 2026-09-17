# ARC modern model assumptions

## Claude Opus 4.8

The [original Anthropic announcement](https://www.anthropic.com/news/claude-opus-4-8) identifies `claude-opus-4-8`, states availability on **May 28, 2026**, and describes it as building on Opus 4.7. Native ARC records use that exact endpoint and max effort with adaptive thinking. These records do not establish the number of active parameters. The announcement was independently read through the web source; direct HTML and linked system-card downloads returned 403, recorded without bypassing the restriction.

Use **100B active parameters** as the common Opus/frontier-scale prior, with **25B–400B** sensitivity (0.25–4 times the central compute). This is a deliberately coarse model-class estimate, not an architectural disclosure or a claim that equal branding/pricing establishes equal size. The official lineage gives a reason to retain the existing Opus-scale assumption rather than choosing an unrelated smaller model; it does not narrow the numerical interval. A changed size estimate must change every point for this model consistently.

## Existing Opus 4.6

The candidate retains the production model identity and shared 100B assumption. Native records explicitly identify `claude-opus-4-6`, low effort and a 120,000-token thinking budget. Its February 4 test timestamps are prerelease evaluation times, not a new public release date. The existing February 5 date is not replaced by those timestamps. The public model release and undisclosed-size status, rather than previous task FLOP values, determine this reuse. The same 25B–400B sensitivity illustrates parameter uncertainty here.
