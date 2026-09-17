## agen-metr3-atariepochs-dsr1

Task: `local_research/atari_epochs`. Find the Atari epoch count used in the original PPO paper, using supplied local papers/webpages; return only the answer.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research/local_research.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 4 successful. Run IDs: mp4-server_354150, mp4-server_355697, mp4-server_355698, mp4-server_355699, mp4-server_355700, mp4-server_355701, mp4-server_355702, mp4-server_355703.
Native tokens by run, in that order: 119462.0, 135729.0, 197792.0, 89592.0, 276833.0, 85475.0, 181057.0, 74031.0.
Arithmetic: sum(tokens) / 8 = 144996; times 7.4e+10 FLOPs/token = 1.07297e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 4 successful / 4 total; successful run IDs: 489, 490, 491, 492.
Published successful geometric-mean rating: 6.393 minutes × 60 = 383.58 seconds.
Released successful pseudo-timestamp durations (seconds): [60.0, 120.0, 300.0, 6300.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Exact-answer question: all four recorded humans answered correctly, while AI succeeds only in half or two-thirds of its runs; this is a substantive answer-reliability deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-atariepochs-oss120b

Task: `local_research/atari_epochs`. Find the Atari epoch count used in the original PPO paper, using supplied local papers/webpages; return only the answer.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research/local_research.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 4 successful. Run IDs: mp4-server_509241, mp4-server_509242, mp4-server_509243, mp4-server_509244, mp4-server_509245, mp4-server_512427.
Native tokens by run, in that order: 1905200.0, 428718.0, 1002732.0, 835568.0, 138700.0, 444642.0.
Arithmetic: sum(tokens) / 6 = 792593; times 1.02e+10 FLOPs/token = 8.08445e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 4 successful / 4 total; successful run IDs: 489, 490, 491, 492.
Published successful geometric-mean rating: 6.393 minutes × 60 = 383.58 seconds.
Released successful pseudo-timestamp durations (seconds): [60.0, 120.0, 300.0, 6300.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Exact-answer question: all four recorded humans answered correctly, while AI succeeds only in half or two-thirds of its runs; this is a substantive answer-reliability deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-blackboxapple-dsr1

Task: `blackbox/apple`. Infer and implement the hidden function for blackbox/apple using queries; meet the task scoring threshold, which rewards economical querying.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 0 successful. Run IDs: mp4-server_354081, mp4-server_355214, mp4-server_355215, mp4-server_355216, mp4-server_355217, mp4-server_355218, mp4-server_355219, mp4-server_355220.
Native tokens by run, in that order: 428809.0, 190026.0, 433229.0, 366041.0, 186176.0, 281633.0, 408184.0, 371431.0.
Arithmetic: sum(tokens) / 8 = 333191; times 7.4e+10 FLOPs/token = 2.46561e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 3 successful / 7 total; successful run IDs: 165, 166, 169.
Published successful geometric-mean rating: 17.6 minutes × 60 = 1056 seconds.
Released successful pseudo-timestamp durations (seconds): [720.0, 960.0, 1620.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Neither model reaches the success criterion; humans reach it in three of seven runs and have higher mean continuous score (0.576 versus approximately 0.38). Both endpoints support a deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-blackboxapple-oss120b

Task: `blackbox/apple`. Infer and implement the hidden function for blackbox/apple using queries; meet the task scoring threshold, which rewards economical querying.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 0 successful. Run IDs: mp4-server_508800, mp4-server_508801, mp4-server_508802, mp4-server_508803, mp4-server_508804, mp4-server_508805.
Native tokens by run, in that order: 254875.0, 203580.0, 177355.0, 223856.0, 263578.0, 221002.0.
Arithmetic: sum(tokens) / 6 = 224041; times 1.02e+10 FLOPs/token = 2.28522e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 3 successful / 7 total; successful run IDs: 165, 166, 169.
Published successful geometric-mean rating: 17.6 minutes × 60 = 1056 seconds.
Released successful pseudo-timestamp durations (seconds): [720.0, 960.0, 1620.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Neither model reaches the success criterion; humans reach it in three of seven runs and have higher mean continuous score (0.576 versus approximately 0.38). Both endpoints support a deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-blackboxcharm-dsr1

Task: `blackbox/charm`. Infer and implement the hidden function for blackbox/charm using queries; meet the task scoring threshold, which rewards economical querying.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 5 successful. Run IDs: mp4-server_354084, mp4-server_355235, mp4-server_355237, mp4-server_355238, mp4-server_355239, mp4-server_355240, mp4-server_355241, mp4-server_356414.
Native tokens by run, in that order: 595824.0, 448116.0, 654950.0, 444402.0, 438618.0, 2899910.0, 337123.0, 431628.0.
Arithmetic: sum(tokens) / 8 = 781321; times 7.4e+10 FLOPs/token = 5.78178e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 1 successful / 6 total; successful run IDs: 195.
Published successful geometric-mean rating: 63.873 minutes × 60 = 3832.38 seconds.
Released successful pseudo-timestamp durations (seconds): [3780.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: above. R1 succeeds five of eight versus one of six human attempts, and mean continuous score also favors R1 (0.819 versus 0.729). The large completion-rate advantage, supported by graded performance, supports above for these recorded baseliners. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-blackboxcharm-oss120b

Task: `blackbox/charm`. Infer and implement the hidden function for blackbox/charm using queries; meet the task scoring threshold, which rewards economical querying.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 0 successful. Run IDs: mp4-server_508821, mp4-server_508822, mp4-server_508824, mp4-server_508825, mp4-server_508826, mp4-server_508827.
Native tokens by run, in that order: 398887.0, 454030.0, 448148.0, 425059.0, 2210581.0, 434947.0.
Arithmetic: sum(tokens) / 6 = 728609; times 1.02e+10 FLOPs/token = 7.43181e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 1 successful / 6 total; successful run IDs: 195.
Published successful geometric-mean rating: 63.873 minutes × 60 = 3832.38 seconds.
Released successful pseudo-timestamp durations (seconds): [3780.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. OSS has no successful run and continuous mean 0.417, versus one of six human successes and mean 0.729; substantial score deficit supports below even though both binary rates are low. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-broccollatz-dsr1

Task: `esolang/broccoli_collatz`. Infer the Broccoli language from examples and an interpreter, then submit a program returning the Collatz step count to reach 1; interpreter reverse engineering is prohibited.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/esolang/README.md. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 1 successful. Run IDs: mp4-server_354104, mp4-server_355375, mp4-server_355376, mp4-server_355377, mp4-server_355378, mp4-server_355379, mp4-server_355380, mp4-server_356823.
Native tokens by run, in that order: 755063.0, 7500377.0, 8060931.0, 1962356.0, 8112050.0, 358579.0, 8116448.0, 7423486.0.
Arithmetic: sum(tokens) / 8 = 5.28616e+06; times 7.4e+10 FLOPs/token = 3.91176e+17 FLOPs.
Fatal-error labels, retained in the computation: {None: 5, 'usageLimits': 3}.

Human records: 5 successful / 6 total; successful run IDs: 372, 373, 374, 375, 377.
Published successful geometric-mean rating: 35.078 minutes × 60 = 2104.68 seconds.
Released successful pseudo-timestamp durations (seconds): [840.0, 1200.0, 1260.0, 1920.0, 15840.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. The coding solution passes in one or two AI runs, versus five of six human runs. This large difference supports below on the same program-correctness criterion. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-broccollatz-oss120b

Task: `esolang/broccoli_collatz`. Infer the Broccoli language from examples and an interpreter, then submit a program returning the Collatz step count to reach 1; interpreter reverse engineering is prohibited.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/esolang/README.md. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 2 successful. Run IDs: mp4-server_508942, mp4-server_508943, mp4-server_508944, mp4-server_508945, mp4-server_508946, mp4-server_508947.
Native tokens by run, in that order: 6429626.0, 8042805.0, 8055409.0, 7287023.0, 8111714.0, 8148937.0.
Arithmetic: sum(tokens) / 6 = 7.67925e+06; times 1.02e+10 FLOPs/token = 7.83284e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 2, 'usageLimits': 4}.

Human records: 5 successful / 6 total; successful run IDs: 372, 373, 374, 375, 377.
Published successful geometric-mean rating: 35.078 minutes × 60 = 2104.68 seconds.
Released successful pseudo-timestamp durations (seconds): [840.0, 1200.0, 1260.0, 1920.0, 15840.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. The coding solution passes in one or two AI runs, versus five of six human runs. This large difference supports below on the same program-correctness criterion. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ecombiggest-dsr1

Task: `interpret_data/ecommerce_biggest_order`. Analyze the supplied e-commerce transaction data and identify its biggest order; submit the task-scored answer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 8 successful. Run IDs: mp4-server_354113, mp4-server_355438, mp4-server_355439, mp4-server_355440, mp4-server_355441, mp4-server_355442, mp4-server_355443, mp4-server_355444.
Native tokens by run, in that order: 63767.0, 55695.0, 78620.0, 103009.0, 44563.0, 48498.0, 62883.0, 49783.0.
Arithmetic: sum(tokens) / 8 = 63352.2; times 7.4e+10 FLOPs/token = 4.68807e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 3 successful / 3 total; successful run IDs: 479, 480, 481.
Published successful geometric-mean rating: 10.735 minutes × 60 = 644.1 seconds.
Released successful pseudo-timestamp durations (seconds): [480.0, 480.0, 1020.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All three humans and every AI run answer the data question correctly. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ecombiggest-oss120b

Task: `interpret_data/ecommerce_biggest_order`. Analyze the supplied e-commerce transaction data and identify its biggest order; submit the task-scored answer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_509001, mp4-server_509002, mp4-server_509003, mp4-server_509004, mp4-server_509005, mp4-server_509006.
Native tokens by run, in that order: 94898.0, 84305.0, 70324.0, 46405.0, 46561.0, 91031.0.
Arithmetic: sum(tokens) / 6 = 72254; times 1.02e+10 FLOPs/token = 7.36991e+14 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 3 successful / 3 total; successful run IDs: 479, 480, 481.
Published successful geometric-mean rating: 10.735 minutes × 60 = 644.1 seconds.
Released successful pseudo-timestamp durations (seconds): [480.0, 480.0, 1020.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All three humans and every AI run answer the data question correctly. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-envsci3-dsr1

Task: `env_scientist/level3`. Discover the rules of the level-3 deterministic binary-grid puzzle through experiments and make predictions meeting the task threshold.
Task-definition locator: https://github.com/METR/public-tasks/blob/5418666a1b026fe4d9b4203751ddb913bf949721/README.md#efficiently-discover-rules-of-grid-environments. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 8 successful. Run IDs: mp4-server_354097, mp4-server_355326, mp4-server_355327, mp4-server_355328, mp4-server_355329, mp4-server_355330, mp4-server_355331, mp4-server_355332.
Native tokens by run, in that order: 222398.0, 230405.0, 376730.0, 375262.0, 194314.0, 370276.0, 156573.0, 339619.0.
Arithmetic: sum(tokens) / 8 = 283197; times 7.4e+10 FLOPs/token = 2.09566e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 1 successful / 2 total; successful run IDs: 350.
Published successful geometric-mean rating: 90.457 minutes × 60 = 5427.42 seconds.
Released successful pseudo-timestamp durations (seconds): [5400.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. Both human runs and every AI run score approximately 0.99–1.0 continuously. The human one-of-two binary result reflects a tight threshold, not a substantive prediction-quality deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-envsci3-oss120b

Task: `env_scientist/level3`. Discover the rules of the level-3 deterministic binary-grid puzzle through experiments and make predictions meeting the task threshold.
Task-definition locator: https://github.com/METR/public-tasks/blob/5418666a1b026fe4d9b4203751ddb913bf949721/README.md#efficiently-discover-rules-of-grid-environments. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_508900, mp4-server_508901, mp4-server_508902, mp4-server_508903, mp4-server_508904, mp4-server_508905.
Native tokens by run, in that order: 147636.0, 139439.0, 213929.0, 197908.0, 250378.0, 187474.0.
Arithmetic: sum(tokens) / 6 = 189461; times 1.02e+10 FLOPs/token = 1.9325e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 1 successful / 2 total; successful run IDs: 350.
Published successful geometric-mean rating: 90.457 minutes × 60 = 5427.42 seconds.
Released successful pseudo-timestamp durations (seconds): [5400.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. Both human runs and every AI run score approximately 0.99–1.0 continuously. The human one-of-two binary result reflects a tight threshold, not a substantive prediction-quality deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-envsci6-dsr1

Task: `env_scientist/level6`. Discover the rules of the level-6 deterministic binary-grid puzzle through experiments and make predictions meeting the task threshold.
Task-definition locator: https://github.com/METR/public-tasks/blob/5418666a1b026fe4d9b4203751ddb913bf949721/README.md#efficiently-discover-rules-of-grid-environments. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 0 successful. Run IDs: mp4-server_354100, mp4-server_355347, mp4-server_355348, mp4-server_355350, mp4-server_355351, mp4-server_356422, mp4-server_356423, mp4-server_357029.
Native tokens by run, in that order: 8246848.0, 8006671.0, 8059472.0, 8177976.0, 8122645.0, 8330321.0, 8143186.0, 8077846.0.
Arithmetic: sum(tokens) / 8 = 8.14562e+06; times 7.4e+10 FLOPs/token = 6.02776e+17 FLOPs.
Fatal-error labels, retained in the computation: {'usageLimits': 8}.

Human records: 2 successful / 3 total; successful run IDs: 358, 359.
Published successful geometric-mean rating: 171.412 minutes × 60 = 10284.7 seconds.
Released successful pseudo-timestamp durations (seconds): [8880.0, 11880.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Humans score about 0.667 on average and two of three succeed; AI means are 0 or 0.166 with zero or one success. Binary and continuous evidence agree. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-envsci6-oss120b

Task: `env_scientist/level6`. Discover the rules of the level-6 deterministic binary-grid puzzle through experiments and make predictions meeting the task threshold.
Task-definition locator: https://github.com/METR/public-tasks/blob/5418666a1b026fe4d9b4203751ddb913bf949721/README.md#efficiently-discover-rules-of-grid-environments. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 1 successful. Run IDs: mp4-server_508918, mp4-server_508919, mp4-server_508920, mp4-server_508921, mp4-server_508922, mp4-server_508923.
Native tokens by run, in that order: 4816012.0, 8138355.0, 8164095.0, 8050850.0, 8146791.0, 8208119.0.
Arithmetic: sum(tokens) / 6 = 7.58737e+06; times 1.02e+10 FLOPs/token = 7.73912e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 1, 'usageLimits': 5}.

Human records: 2 successful / 3 total; successful run IDs: 358, 359.
Published successful geometric-mean rating: 171.412 minutes × 60 = 10284.7 seconds.
Released successful pseudo-timestamp durations (seconds): [8880.0, 11880.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Humans score about 0.667 on average and two of three succeed; AI means are 0 or 0.166 with zero or one success. Binary and continuous evidence agree. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-luhndigits-dsr1

Task: `credit_card_validity/add_check_digits`. Compute and add Luhn check digits for the supplied card-number inputs; produce the output accepted by the task scorer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 1.0.2-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 7 successful. Run IDs: mp4-server_354090, mp4-server_355277, mp4-server_355278, mp4-server_355279, mp4-server_355280, mp4-server_355281, mp4-server_355282, mp4-server_355283.
Native tokens by run, in that order: 121965.0, 97200.0, 102823.0, 90454.0, 160544.0, 149132.0, 97308.0, 139700.0.
Arithmetic: sum(tokens) / 8 = 119891; times 7.4e+10 FLOPs/token = 8.87192e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 3 successful / 4 total; successful run IDs: 219, 221, 222.
Published successful geometric-mean rating: 26.948 minutes × 60 = 1616.88 seconds.
Released successful pseudo-timestamp durations (seconds): [780.0, 1860.0, 2700.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. R1 passes seven of eight runs and humans three of four; both usually deliver valid outputs. This limited sample does not suggest a material capability difference. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-luhndigits-oss120b

Task: `credit_card_validity/add_check_digits`. Compute and add Luhn check digits for the supplied card-number inputs; produce the output accepted by the task scorer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 1.0.2-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 3 successful. Run IDs: mp4-server_508858, mp4-server_508859, mp4-server_508860, mp4-server_508861, mp4-server_508862, mp4-server_508863.
Native tokens by run, in that order: 38298.0, 37283.0, 35743.0, 30919.0, 43477.0, 34197.0.
Arithmetic: sum(tokens) / 6 = 36652.8; times 1.02e+10 FLOPs/token = 3.73859e+14 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 3 successful / 4 total; successful run IDs: 219, 221, 222.
Published successful geometric-mean rating: 26.948 minutes × 60 = 1616.88 seconds.
Released successful pseudo-timestamp durations (seconds): [780.0, 1860.0, 2700.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. OSS passes only three of six versus three of four human attempts. Half of model outputs fail the validity target, giving a tentative reliability deficit rather than treating selected successful human timings as perfect reliability. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mungetraj-dsr1

Task: `munge_data/trajectories`. Write and apply a conversion script for supplied trajectory JSON data, inferring the transformation from examples; satisfy the task scorer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 1.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 0 successful. Run IDs: mp4-server_354119, mp4-server_355482, mp4-server_355484, mp4-server_356440, mp4-server_356441, mp4-server_356442, mp4-server_356443, mp4-server_356444.
Native tokens by run, in that order: 1186197.0, 3659654.0, 8062659.0, 2444896.0, 7562460.0, 8071278.0, 7533039.0, 3576365.0.
Arithmetic: sum(tokens) / 8 = 5.26207e+06; times 7.4e+10 FLOPs/token = 3.89393e+17 FLOPs.
Fatal-error labels, retained in the computation: {None: 6, 'usageLimits': 2}.

Human records: 2 successful / 3 total; successful run IDs: 596, 598.
Published successful geometric-mean rating: 129.285 minutes × 60 = 7757.1 seconds.
Released successful pseudo-timestamp durations (seconds): [6060.0, 9900.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Both models fail every run whereas two of three human attempts pass the conversion scorer. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mungetraj-oss120b

Task: `munge_data/trajectories`. Write and apply a conversion script for supplied trajectory JSON data, inferring the transformation from examples; satisfy the task scorer.
Task-definition locator: https://arxiv.org/html/2503.17354v1#S6. The release is descriptive evidence; exact run versions are 1.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 0 successful. Run IDs: mp4-server_509037, mp4-server_509038, mp4-server_509039, mp4-server_509041, mp4-server_509042, mp4-server_509043.
Native tokens by run, in that order: 8041838.0, 8017774.0, 8084421.0, 8087298.0, 8014694.0, 8019538.0.
Arithmetic: sum(tokens) / 6 = 8.04426e+06; times 1.02e+10 FLOPs/token = 8.20515e+16 FLOPs.
Fatal-error labels, retained in the computation: {'usageLimits': 6}.

Human records: 2 successful / 3 total; successful run IDs: 596, 598.
Published successful geometric-mean rating: 129.285 minutes × 60 = 7757.1 seconds.
Released successful pseudo-timestamp durations (seconds): [6060.0, 9900.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. Both models fail every run whereas two of three human attempts pass the conversion scorer. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mysteryfn4-dsr1

Task: `hypothesis_testing/mystery_function_4`. Query mystery_function_4 without reading its implementation and select the correct hypothesis from the supplied list; return the hypothesis letter.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/hypothesis_testing/README.md. The release is descriptive evidence; exact run versions are 0.1.2-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 7 successful. Run IDs: mp4-server_354109, mp4-server_355410, mp4-server_355411, mp4-server_355412, mp4-server_355413, mp4-server_355414, mp4-server_355415, mp4-server_355416.
Native tokens by run, in that order: 236152.0, 293386.0, 194355.0, 181555.0, 197138.0, 1056718.0, 372268.0, 501537.0.
Arithmetic: sum(tokens) / 8 = 379139; times 7.4e+10 FLOPs/token = 2.80563e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 3 successful / 3 total; successful run IDs: 433, 434, 435.
Published successful geometric-mean rating: 10.153 minutes × 60 = 609.18 seconds.
Released successful pseudo-timestamp durations (seconds): [420.0, 540.0, 900.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All three humans and most AI runs identify the correct hypothesis (seven of eight or five of six). Occasional errors in these small samples do not establish a noticeably different problem-solving level. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mysteryfn4-oss120b

Task: `hypothesis_testing/mystery_function_4`. Query mystery_function_4 without reading its implementation and select the correct hypothesis from the supplied list; return the hypothesis letter.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/hypothesis_testing/README.md. The release is descriptive evidence; exact run versions are 0.1.2-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 5 successful. Run IDs: mp4-server_508972, mp4-server_508973, mp4-server_508974, mp4-server_508975, mp4-server_508976, mp4-server_508977.
Native tokens by run, in that order: 1337715.0, 67825.0, 319477.0, 453938.0, 65340.0, 4638401.0.
Arithmetic: sum(tokens) / 6 = 1.14712e+06; times 1.02e+10 FLOPs/token = 1.17006e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 3 successful / 3 total; successful run IDs: 433, 434, 435.
Published successful geometric-mean rating: 10.153 minutes × 60 = 609.18 seconds.
Released successful pseudo-timestamp durations (seconds): [420.0, 540.0, 900.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All three humans and most AI runs identify the correct hypothesis (seven of eight or five of six). Occasional errors in these small samples do not establish a noticeably different problem-solving level. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mysteryfn8-dsr1

Task: `hypothesis_testing/mystery_function_8`. Query mystery_function_8 without reading its implementation and select the correct hypothesis from the supplied list; return the hypothesis letter.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/hypothesis_testing/README.md. The release is descriptive evidence; exact run versions are 0.1.2-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 5 successful. Run IDs: mp4-server_354112, mp4-server_355431, mp4-server_355432, mp4-server_355433, mp4-server_355434, mp4-server_355435, mp4-server_355436, mp4-server_355437.
Native tokens by run, in that order: 482081.0, 185363.0, 375090.0, 68078.0, 60066.0, 738713.0, 98527.0, 176687.0.
Arithmetic: sum(tokens) / 8 = 273076; times 7.4e+10 FLOPs/token = 2.02076e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 3 successful / 3 total; successful run IDs: 443, 444, 445.
Published successful geometric-mean rating: 14.773 minutes × 60 = 886.38 seconds.
Released successful pseudo-timestamp durations (seconds): [660.0, 900.0, 1080.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. All three humans identify the hypothesis, but each model fails roughly one-third of its runs. Relative to the small successful human sample, this is a tentative but best-supported reliability deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-mysteryfn8-oss120b

Task: `hypothesis_testing/mystery_function_8`. Query mystery_function_8 without reading its implementation and select the correct hypothesis from the supplied list; return the hypothesis letter.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/hypothesis_testing/README.md. The release is descriptive evidence; exact run versions are 0.1.2-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 4 successful. Run IDs: mp4-server_508990, mp4-server_508991, mp4-server_508993, mp4-server_508995, mp4-server_508997, mp4-server_508999.
Native tokens by run, in that order: 184697.0, 1034151.0, 1525974.0, 241650.0, 515636.0, 90401.0.
Arithmetic: sum(tokens) / 6 = 598752; times 1.02e+10 FLOPs/token = 6.10727e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 3 successful / 3 total; successful run IDs: 443, 444, 445.
Published successful geometric-mean rating: 14.773 minutes × 60 = 886.38 seconds.
Released successful pseudo-timestamp durations (seconds): [660.0, 900.0, 1080.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. All three humans identify the hypothesis, but each model fails roughly one-third of its runs. Relative to the small successful human sample, this is a tentative but best-supported reliability deficit. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ormallbugs-dsr1

Task: `debug_small_libs/orm_allbugs`. Repair the supplied ORM-library variant orm_allbugs until the required tests pass; preserve test files and submit the repaired code.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/debug_small_libs/debug_small_libs.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 5 successful. Run IDs: mp4-server_354093, mp4-server_355298, mp4-server_355299, mp4-server_355300, mp4-server_355301, mp4-server_355302, mp4-server_355304, mp4-server_356415.
Native tokens by run, in that order: 2635378.0, 8129181.0, 364367.0, 8123226.0, 1719612.0, 863684.0, 8025985.0, 279378.0.
Arithmetic: sum(tokens) / 8 = 3.7676e+06; times 7.4e+10 FLOPs/token = 2.78803e+17 FLOPs.
Fatal-error labels, retained in the computation: {None: 5, 'usageLimits': 3}.

Human records: 24 successful / 30 total; successful run IDs: 238, 239, 240, 241, 242, 243, 244, 246, 247, 248, 249, 251, 252, 253, 254, 256, 257, 258, 259, 260, 262, 263, 265, 267.
Published successful geometric-mean rating: 95.218 minutes × 60 = 5713.08 seconds.
Released successful pseudo-timestamp durations (seconds): [1080.0, 1380.0, 1560.0, 3000.0, 3300.0, 3300.0, 3360.0, 4800.0, 4860.0, 5280.0, 5580.0, 5820.0, 6600.0, 6780.0, 7440.0, 7680.0, 8400.0, 8940.0, 9000.0, 10440.0, 11100.0, 11400.0, 15120.0, 35280.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. Humans pass 24 of 30 runs; R1 passes five of eight and OSS six of six. These modest samples span the human reliability, and the same binary code-correctness criterion is usually met. Broad comparability is more defensible than claiming a distinct capability level. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ormallbugs-oss120b

Task: `debug_small_libs/orm_allbugs`. Repair the supplied ORM-library variant orm_allbugs until the required tests pass; preserve test files and submit the repaired code.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/debug_small_libs/debug_small_libs.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_508876, mp4-server_508877, mp4-server_508878, mp4-server_508879, mp4-server_508880, mp4-server_508881.
Native tokens by run, in that order: 549798.0, 780179.0, 366523.0, 469094.0, 849175.0, 489593.0.
Arithmetic: sum(tokens) / 6 = 584060; times 1.02e+10 FLOPs/token = 5.95742e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 24 successful / 30 total; successful run IDs: 238, 239, 240, 241, 242, 243, 244, 246, 247, 248, 249, 251, 252, 253, 254, 256, 257, 258, 259, 260, 262, 263, 265, 267.
Published successful geometric-mean rating: 95.218 minutes × 60 = 5713.08 seconds.
Released successful pseudo-timestamp durations (seconds): [1080.0, 1380.0, 1560.0, 3000.0, 3300.0, 3300.0, 3360.0, 4800.0, 4860.0, 5280.0, 5580.0, 5820.0, 6600.0, 6780.0, 7440.0, 7680.0, 8400.0, 8940.0, 9000.0, 10440.0, 11100.0, 11400.0, 15120.0, 35280.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. Humans pass 24 of 30 runs; R1 passes five of eight and OSS six of six. These modest samples span the human reliability, and the same binary code-correctness criterion is usually met. Broad comparability is more defensible than claiming a distinct capability level. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ormsomebugs-dsr1

Task: `debug_small_libs/orm_somebugs`. Repair the supplied ORM-library variant orm_somebugs until the required tests pass; preserve test files and submit the repaired code.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/debug_small_libs/debug_small_libs.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 8 successful. Run IDs: mp4-server_354094, mp4-server_355305, mp4-server_355306, mp4-server_355308, mp4-server_355309, mp4-server_355310, mp4-server_355311, mp4-server_356416.
Native tokens by run, in that order: 842042.0, 650523.0, 189184.0, 256419.0, 224766.0, 469955.0, 640662.0, 249224.0.
Arithmetic: sum(tokens) / 8 = 440347; times 7.4e+10 FLOPs/token = 3.25857e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 8}.

Human records: 57 successful / 70 total; successful run IDs: 268, 269, 270, 271, 272, 274, 276, 277, 280, 282, 283, 284, 285, 286, 287, 288, 289, 290, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 304, 305, 307, 308, 309, 310, 311, 312, 313, 315, 316, 317, 318, 319, 320, 322, 323, 324, 325, 327, 328, 329, 330, 332, 333, 335, 336, 337.
Published successful geometric-mean rating: 84.437 minutes × 60 = 5066.22 seconds.
Released successful pseudo-timestamp durations (seconds): [0.0, 180.0, 780.0, 1260.0, 1440.0, 1440.0, 1740.0, 1920.0, 2820.0, 3180.0, 3420.0, 3420.0, 3540.0, 3540.0, 3600.0, 3660.0, 3780.0, 3900.0, 4260.0, 4380.0, 4680.0, 4860.0, 5160.0, 5160.0, 5160.0, 5280.0, 5520.0, 5580.0, 5760.0, 5820.0, 5820.0, 6000.0, 6300.0, 6300.0, 6480.0, 6480.0, 6720.0, 7140.0, 7740.0, 7860.0, 8100.0, 8220.0, 8460.0, 8760.0, 9000.0, 9720.0, 9960.0, 10020.0, 11460.0, 12300.0, 12960.0, 13680.0, 15240.0, 20280.0, 22380.0, 81240.0, 131100.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. The models pass every small-sample run, versus 57 of 70 human attempts; the human continuous mean is 0.833. Both usually repair the library successfully; the available model samples support broad comparability without a confident advantage claim. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-ormsomebugs-oss120b

Task: `debug_small_libs/orm_somebugs`. Repair the supplied ORM-library variant orm_somebugs until the required tests pass; preserve test files and submit the repaired code.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/debug_small_libs/debug_small_libs.py. The release is descriptive evidence; exact run versions are 0.1.1-post1-9fe62e8.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_508882, mp4-server_508883, mp4-server_508884, mp4-server_508885, mp4-server_508886, mp4-server_508887.
Native tokens by run, in that order: 478019.0, 405531.0, 811870.0, 536475.0, 880820.0, 526319.0.
Arithmetic: sum(tokens) / 6 = 606506; times 1.02e+10 FLOPs/token = 6.18636e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 57 successful / 70 total; successful run IDs: 268, 269, 270, 271, 272, 274, 276, 277, 280, 282, 283, 284, 285, 286, 287, 288, 289, 290, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 304, 305, 307, 308, 309, 310, 311, 312, 313, 315, 316, 317, 318, 319, 320, 322, 323, 324, 325, 327, 328, 329, 330, 332, 333, 335, 336, 337.
Published successful geometric-mean rating: 84.437 minutes × 60 = 5066.22 seconds.
Released successful pseudo-timestamp durations (seconds): [0.0, 180.0, 780.0, 1260.0, 1440.0, 1440.0, 1740.0, 1920.0, 2820.0, 3180.0, 3420.0, 3420.0, 3540.0, 3540.0, 3600.0, 3660.0, 3780.0, 3900.0, 4260.0, 4380.0, 4680.0, 4860.0, 5160.0, 5160.0, 5160.0, 5280.0, 5520.0, 5580.0, 5760.0, 5820.0, 5820.0, 6000.0, 6300.0, 6300.0, 6480.0, 6480.0, 6720.0, 7140.0, 7740.0, 7860.0, 8100.0, 8220.0, 8460.0, 8760.0, 9000.0, 9720.0, 9960.0, 10020.0, 11460.0, 12300.0, 12960.0, 13680.0, 15240.0, 20280.0, 22380.0, 81240.0, 131100.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. The models pass every small-sample run, versus 57 of 70 human attempts; the human continuous mean is 0.833. Both usually repair the library successfully; the available model samples support broad comparability without a confident advantage claim. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-tex33b65b-dsr1

Task: `local_research_tex/33b_better_than_65b`. Use supplied local paper sources to identify the commonsense-reasoning tasks where LLaMA-33B exceeds LLaMA-65B in zero-shot performance; submit the requested names.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research_tex/local_research_tex.py. The release is descriptive evidence; exact run versions are 1.1.4-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 2 successful. Run IDs: mp4-server_354152, mp4-server_355711, mp4-server_355712, mp4-server_355713, mp4-server_355714, mp4-server_355715, mp4-server_355716, mp4-server_355717.
Native tokens by run, in that order: 8094113.0, 798344.0, 6975581.0, 589392.0, 8063616.0, 910528.0, 435854.0, 960870.0.
Arithmetic: sum(tokens) / 8 = 3.35354e+06; times 7.4e+10 FLOPs/token = 2.48162e+17 FLOPs.
Fatal-error labels, retained in the computation: {'usageLimits': 2, None: 6}.

Human records: 5 successful / 5 total; successful run IDs: 496, 497, 498, 499, 500.
Published successful geometric-mean rating: 24.28 minutes × 60 = 1456.8 seconds.
Released successful pseudo-timestamp durations (seconds): [360.0, 720.0, 1380.0, 3000.0, 5700.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. R1 answers correctly in two of eight runs, versus all five humans; the large exact-answer reliability deficit supports below. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-tex33b65b-oss120b

Task: `local_research_tex/33b_better_than_65b`. Use supplied local paper sources to identify the commonsense-reasoning tasks where LLaMA-33B exceeds LLaMA-65B in zero-shot performance; submit the requested names.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research_tex/local_research_tex.py. The release is descriptive evidence; exact run versions are 1.1.4-post2-92fc96f.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_509253, mp4-server_509254, mp4-server_509255, mp4-server_509256, mp4-server_509257, mp4-server_509258.
Native tokens by run, in that order: 421034.0, 442718.0, 173060.0, 329324.0, 422696.0, 177490.0.
Arithmetic: sum(tokens) / 6 = 327720; times 1.02e+10 FLOPs/token = 3.34275e+15 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 5 successful / 5 total; successful run IDs: 496, 497, 498, 499, 500.
Published successful geometric-mean rating: 24.28 minutes × 60 = 1456.8 seconds.
Released successful pseudo-timestamp durations (seconds): [360.0, 720.0, 1380.0, 3000.0, 5700.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All OSS runs and all recorded human attempts answer the lookup question correctly. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-texarreport-dsr1

Task: `local_research_tex/ar_report`. Use the supplied local AR report to find the number of tasks completed by its best-performing agent; submit the requested number.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research_tex/local_research_tex.py. The release is descriptive evidence; exact run versions are 1.1.4-post1-9fe62e8.

AI alias `DeepSeek-R1`, scaffold `flock-public`; all 8 runs included, 2 successful. Run IDs: mp4-server_354153, mp4-server_355719, mp4-server_355721, mp4-server_355722, mp4-server_355724, mp4-server_356452, mp4-server_356453, mp4-server_356454.
Native tokens by run, in that order: 296442.0, 629377.0, 1399004.0, 1708247.0, 1665949.0, 486221.0, 8031059.0, 256166.0.
Arithmetic: sum(tokens) / 8 = 1.80906e+06; times 7.4e+10 FLOPs/token = 1.3387e+17 FLOPs.
Fatal-error labels, retained in the computation: {None: 7, 'usageLimits': 1}.

Human records: 4 successful / 4 total; successful run IDs: 501, 502, 503, 504.
Published successful geometric-mean rating: 23.678 minutes × 60 = 1420.68 seconds.
Released successful pseudo-timestamp durations (seconds): [660.0, 1320.0, 1800.0, 2460.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: below. R1 answers correctly in two of eight runs, versus all four humans; the large exact-answer reliability deficit supports below. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.

## agen-metr3-texarreport-oss120b

Task: `local_research_tex/ar_report`. Use the supplied local AR report to find the number of tasks completed by its best-performing agent; submit the requested number.
Task-definition locator: https://github.com/METR/hcast-public/blob/main/local_research_tex/local_research_tex.py. The release is descriptive evidence; exact run versions are 1.1.4-post2-92fc96f.

AI alias `gpt-oss-120b`, scaffold `flock-public`; all 6 runs included, 6 successful. Run IDs: mp4-server_509259, mp4-server_509260, mp4-server_509261, mp4-server_509262, mp4-server_509263, mp4-server_509264.
Native tokens by run, in that order: 3295047.0, 1394289.0, 3542032.0, 995805.0, 1624504.0, 2342821.0.
Arithmetic: sum(tokens) / 6 = 2.19908e+06; times 1.02e+10 FLOPs/token = 2.24306e+16 FLOPs.
Fatal-error labels, retained in the computation: {None: 6}.

Human records: 4 successful / 4 total; successful run IDs: 501, 502, 503, 504.
Published successful geometric-mean rating: 23.678 minutes × 60 = 1420.68 seconds.
Released successful pseudo-timestamp durations (seconds): [660.0, 1320.0, 1800.0, 2460.0]. These do not exactly reproduce the published rating; they are retained as an audit cross-check, not substituted for the rating. Source human_source=`baseline`.

Performance classification: match. All OSS runs and all recorded human attempts answer the lookup question correctly. All recorded human outcomes define performance; successful human timing selection does not imply perfect reliability.
