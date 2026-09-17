# DAVE-2 lane-following steering

## physical-dave2-steering-minute

This point represents one minute of continuous lane-following steering on roads of the kind tested in the original NVIDIA study. It excludes lane changes, turns between roads, speed control, navigation and collecting driving data. A licensed human driver spends the same 60 seconds steering; the duration is defined by this real-time work unit, not an observed completion-time sample.

[Bojarski et al. (2016)](https://arxiv.org/abs/1604.07316), Section 2 and Figure 3, describes a single front-facing camera driving the trained CNN and a drive-by-wire steering interface. Three cameras are used for training augmentation, not three inference networks. The abstract reports operation at 30 frames per second. Figure 4 reports approximately 27 million connections and 250,000 learned parameters. Convolutional weights are reused spatially, so multiplying parameter count by two would substantially undercount a frame.

The dominant multiply-add count is:

`27,000,000 connections/frame × 2 FLOPs/connection × 30 frames/second × 60 seconds = 97,200,000,000 FLOPs`.

This is a rounded architecture-based forward estimate, not GPU peak throughput or training compute. It includes the convolutional and dense layers covered by the source connection count. Image normalization, scalar activations, camera conversion and drive-by-wire bookkeeping are not exhaustively counted; they do not justify treating GPU capacity as actual FLOPs. The source input is 66×200×3. The figure's flattened-width label of 1,164 disagrees with its displayed 64×1×18 feature map (1,152); using the source's rounded connection total avoids claiming a false exact architecture reconstruction. The difference in the first dense layer is tiny relative to the approximately 27 million connections. A manual layer check using the displayed convolution maps and a 1,152-wide flatten gives 26,876,342 multiply-add connections per frame, within 0.5% of the rounded source total. A 26–28 million connection range gives 93.6–100.8 billion FLOPs per minute.

The model record names the original DAVE-2 system, rather than a later PilotNet revision or third-party reimplementation. The paper does not establish public availability of the trained checkpoint, so the release date is blank. This non-token model has no shared FLOPs-per-token coefficient. Its reported 250,000 parameters are contextual; the compute recipe uses executed connections, not that parameter count.

### Performance and human comparison

Section 7.2 reports approximately 98% autonomous steering time on a typical Holmdel-to-Atlantic Highlands route. Lane changes and turns between roads are explicitly excluded. A separate 10-mile Garden State Parkway drive had zero interventions. These are reported road tests, not a 98% probability of succeeding on an arbitrary one-minute trial. The simulated six-second intervention penalty in Section 7.1 is a different measure and is not used as human time.

Classify performance as below an ordinary licensed driver for lane following under these conditions: the source system still needs a human to take over part of the time, and the study identifies robustness as unfinished work. This is a substantive comparison, not a measured paired human success rate or a claim that humans never make errors. The narrow highway demonstration supports successful steering, but it does not establish parity across the broader tested roads.

Humans see the road directly and have normal peripheral and vehicle-motion information; the network uses a cropped forward-camera image. This difference is flagged. Throttle and route choice are outside both stated work units. Human practice and the AI's prior training are excluded from this inference point. There is no timing or attempt sample behind the defined 60-second unit, and no claim to reconstruct a selected minute of native policy calls.
