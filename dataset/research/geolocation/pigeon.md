# PIGEON: one GeoGuessr location guess

## perc-geoguessr-pigeon

The work unit is one coordinate guess in the paper’s live Competitive Duels evaluation. It is not one whole match or generic geolocation of an arbitrary photograph. The original CVPR paper Figure 4 shows median error 73 km for PIGEON and 151 km for Champion-division humans across 458 multi-round matches. This supports above relative to expert players. The chart pools PIGEON’s results across opponent levels, so it is not a matched Champion-only effect size. Do not substitute the separate 5,000-location holdout result.

Human time is an assumed **30 active seconds per guess**. The supplement H.2 gives the second player up to 15 seconds after the first guess. The released bot code provides a more concrete estimate of the time before that window: `bot/chrome_extension/scripts/duel.js` waits a uniformly sampled 2–9 seconds, then waits 1.25 + 0.25 seconds for each of four image captures. This is 8–15 seconds before network, inference and other unmeasured overhead, with an expected programmed delay of 11.5 seconds. Adding the 15-second response window gives 26.5 seconds before overhead; round to 30 seconds.

This estimate assumes the released bot timing represents the live experiment, the bot generally guesses first, and the human works throughout the available time. The code does not measure human active time or establish those assumptions. Humans can submit before the bot or before the deadline. Use 5–60 seconds as an early-submission/delay sensitivity scenario, not a confidence interval. If the human guesses first, the released bot is subject to the response window instead. The estimate describes expert play at the reported human quality, not time to reach PIGEON’s lower error. `agent-work/sources/geolocation/bot__chrome_extension__scripts__duel.js` is retained at commit `561f7edf4f61d61d2862f2947a8f8b68892bfcfc`, SHA-256 `e220af9ebbd86daa364b8796b7ab3afa751ea87353f0d5cfe09b559f8c18267e`; see `agent-work/sources/geolocation/bot-source-manifest.json` for original URLs and hashes.

Humans can move through Street View while PIGEON uses four fixed views. This is the concrete inputs/tools difference. The pooled AI and Champion-only human aggregates use different evaluation sets, so `different_assessment` also applies. The supplement reports 1.8% of live locations within 100m of training locations; that is not a count of identical test images. Experienced humans can also have seen locations. No additional blanket assessment flag is inferred solely from that overlap. Exact round counts and human timing samples are not published; the architecture-based point estimate does not claim 458 sampled attempts per guess.

## Reproduction

Run `python3 -B count_pigeon.py SOURCE_DIR OUTPUT_JSON` with Python 3 (standard library only). `SOURCE_DIR` must contain the retained `clip-config.json` and `bot__chrome_extension__scripts__duel.js`. For example, from the published dataset root:

```sh
python3 -B research/geolocation/count_pigeon.py agent-work/sources/geolocation /tmp/pigeon-recomputed.json
```

Choose a new output path outside the sources directory. The calculator reads the explicit programmed delays from the bot file, records input hashes and writes the compute count and timing assumptions. It refuses to overwrite any existing file or write inside the evidence directory. `calculations.json` is the retained result.

## Compute reconstruction

Original public code is pinned to commit 561f7edf4f61d61d2862f2947a8f8b68892bfcfc. `super_guessr.py` reshapes each panorama into four 336×336 inputs and averages their 1024-dimensional embeddings before its 2203-cell linear head. `proto_refiner.py` searches the five selected geocells and stored cluster/member embeddings. Stored embeddings are reused; their initial generation is preparation, not recomputed for every guess. No text encoder is used at inference.

`count_pigeon.py SOURCE_DIR OUTPUT_JSON` uses the retained CLIP ViT-L/14-336 configuration. It counts patch projection, 24 transformer layers including bidirectional attention, approximate activation/normalization arithmetic and the output head, at two operations per MAC. Per image is 383.286 GFLOPs; four images plus the head are 1.53315 TFLOPs. Even searching the full approximate 100,000-panorama training set twice for cluster/member distances and averaging all four-view member vectors adds only 1.024 GFLOPs. This conservative retrieval allowance rounds with the neural work to **1.53e12 FLOPs**. Exact selected cluster sizes, auxiliary heads and scalar geographic postprocessing do not materially affect that rounded estimate. This is calculated supported architecture/workload, not measured runtime converted into FLOPs. The omitted arithmetic is below the precision claimed; decoded image handling and browser rendering are outside AI model compute.

The public repository does not release the trained model weights, so no public model release date is inferred from the paper or code publication date. The disclosed inference architecture is adequate for this operation count; it does not permit reproducing the paper’s predictions.

Sources: [original CVPR paper](https://openaccess.thecvf.com/content/CVPR2024/papers/Haas_PIGEON_Predicting_Image_Geolocations_CVPR_2024_paper.pdf), Figure 4 and model description; [supplement](https://openaccess.thecvf.com/content/CVPR2024/supplemental/Haas_PIGEON_Predicting_Image_CVPR_2024_supplemental.pdf), Tables 5–6 and H.1–H.3; [author code](https://github.com/LukasHaas/PIGEON/tree/561f7edf4f61d61d2862f2947a8f8b68892bfcfc); [original bot delays](https://github.com/LukasHaas/PIGEON/blob/561f7edf4f61d61d2862f2947a8f8b68892bfcfc/bot/chrome_extension/scripts/duel.js#L13-L48); [CLIP configuration](https://huggingface.co/openai/clip-vit-large-patch14-336/blob/main/config.json). Retained originals and calculator inputs are in agent-work/sources/.
