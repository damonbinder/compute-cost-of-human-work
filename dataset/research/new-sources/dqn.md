# DQN Atari: initial tranche

Original source: [Mnih et al., Nature 2015](https://deepmind-media.storage.googleapis.com/dqn/DQNNaturePaper.pdf), Methods neural network architecture, frame skipping and evaluation; Figure 3. This note was reconstructed from the original paper, without prior dataset values.

Reported inputs: 84×84×4 image stack; convolution layers 32 filters 8×8 stride 4, 64 filters 4×4 stride 2, 64 filters 3×3 stride 1; hidden fully connected layer 512. Games run at 60Hz, with decisions every fourth frame. Evaluation epsilon is .05. Human is a professional tester, same emulator, no audio. Figure 3 places Pong near the human baseline and Breakout far above it. The human practices about two hours per game. Evaluation episode caps are not actual episode durations.

## Computation

One forward pass, counting a multiplication and addition separately, is

`2 × (20×20×32×8×8×4 + 9×9×64×4×4×32 + 7×7×64×3×3×64 + 3136×512 + 512×A)`.

Use A=6 for Pong and A=4 for Breakout, the legal action set sizes for these Atari games. These affect less than .02% of the result; 18 outputs would be immaterial. ReLU, bias additions and preprocessing are omitted because the matrix/convolution multiplications dominate. A one-minute unit gives 60×60/4=900 decisions. Multiply by .95 for the nonrandom decisions; the [official DeepMind implementation](https://raw.githubusercontent.com/google-deepmind/dqn/master/dqn/NeuralQLearner.lua), eGreedy/greedy, confirms that random actions bypass the neural forward call.

Human duration is 60 seconds of active real-time play by definition. It is a work-rate normalization of the reported real-time protocol, not a statistical episode duration. No count of recorded attempts is assigned to this analytic segment. Episode scoring supports the policy-quality comparison, not a measured score on each arbitrary segment. This unit remains useful for sustained motor/visual control; users should not interpret it as time to finish a game.

## dqn_pong_minute

A=6 gives 18,692,096 FLOPs/forward; ×855 = 15,981,742,080 FLOPs. Human 60s. Performance match from Figure 3.

## dqn_breakout_minute

A=4 gives 18,690,048 FLOPs/forward; ×855 = 15,979,991,040 FLOPs. Human 60s. Performance above from Figure 3 and Methods discussion.

Learning comparison is deferred: the paper's 50 million decision frames correspond to 38 simulated days, not 9.6 days. A proper full-training reconstruction must add minibatch forward/backward, target-network passes, rollout calls and validation. The two-hour professional practice period is not ordinary people's time to learn from general novice status.
