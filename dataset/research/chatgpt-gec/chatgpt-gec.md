# One ChatGPT grammar correction with an exact human timing

## writing-chatgpt-gec-conll14-17

This point joins the source sentence printed in [Wu et al., Table 4](https://arxiv.org/abs/2303.13648) to the exact same sentence in the original [PEET timing dataset](https://github.com/ankitvad/PEET_Scorer/tree/7d2330909212f0bdc0d29b2a1ccc4d120a6d7a21). The work is correcting one awkward sentence about exercise and family disease risk. It is an illustrative example chosen by the ChatGPT paper's authors, not a random sample or an average editing task.

### Human observation and quality

Original record `C14_17_S` contains the identical source string, a professional editor's correction, and **120.976 seconds**. The `_S` suffix identifies unaided source correction. The `_G` and `_P` records concern editing already-corrected model outputs and are excluded. We use the raw `Time`, not a merged timing across conditions. The row passes the source's 250-second filter. `extract_timing.py` reads the original pickle through an allowlist of data constructors; its Git object hash matches the pinned repository tree. This is one actual timing observation, not a duration inferred from word count.

[The timing study](https://arxiv.org/html/2510.04394v1), Section 3.2, used professional Scribendi editors, one per sentence condition. The instruction was to make minimal corrections. Qualtrics measured the interval spent reading and editing; the released metadata cannot distinguish a pause from active deliberation. No unsupported pause subtraction is made.

The printed ChatGPT output removes the incorrect article, repairs the exercise phrase and makes the family-disease wording more fluent. The timed editor also repairs the article and exercise phrase, interpreting the disease phrase as genetic disease. Both make an interpretive choice in an unclear sentence. The AI paraphrases more freely, including changing chances to opportunities and adding prevention language; the human preserves more wording under the minimal-edit instruction. Broadly comparable grammatical correction is the best-supported judgment for this particular pair. This is a reviewer judgment from the actual outputs, not the paper's benchmark F-score treated as a human success probability. It does not assert identical meaning or perfect editing. No material task-input difference is identified: both receive the same sentence and are asked to correct its English.

### AI workload

The original paper manually queried early ChatGPT and states that its printed correction instruction was used for each test sample. The paper predates a meaningful GPT-4 evaluation and describes the GPT-3.5/InstructGPT lineage; the old inventory's GPT-4 attribution is unsupported. Use the shared early-ChatGPT model record, including its explicit 175B GPT-3-scale parameter proxy. The source does not disclose an exact backend revision.

The Table 4 source and output were checked in the rendered PDF. `inputs.json` records their transcriptions and the Section 3.1 instruction. Retokenization with the retained cl100k vocabulary gives **43 instruction-plus-source tokens and 26 printed answer tokens**. The public report omits the chat system prompt, framing and any surrounding response prose. Central accounting adds **32 system/framing tokens and 10 unprinted response tokens**, giving **111 tokens** and **38.85 trillion FLOPs** at the shared 350 billion FLOPs/token coefficient. These allowances are estimates for a short, independent editing query; they are not native usage counters.

The printed text alone costs 24.15 trillion FLOPs. Another 100 system/history tokens raise the total to 73.85 trillion; one full additional attempt doubles it to 77.7 trillion. Exact conversation resets, earlier context and retry history are unavailable. The central estimate follows the paper's per-sample prompt description, with a fresh query and no unseen retry; it is not a recovered complete service trace. No prompt-search experiment is allocated to this particular correction. Model size, hidden framing and possible conversational context dominate compute uncertainty.

### Reproduction

Run `extract_timing.py --source SOURCES/combined_dataframe.pkl --output NEW_TIMING.json` with pandas and NumPy. Then run `recompute.py --sources SOURCES --inputs inputs.json --timing NEW_TIMING.json --models model-inputs.csv --output NEW_CALCULATIONS.json` with tiktoken. Both require new output files outside the source directory. No model or API is executed. The source sentence is checked for exact equality between the two studies.
