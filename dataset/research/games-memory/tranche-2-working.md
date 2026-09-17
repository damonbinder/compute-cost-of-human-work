# Tranche 2 research in progress

MuZero: original Mnih Methods directly confirms around two hours of practice per game by the professional tester, followed by around20 episodes capped at5min. This supports a 7200-second game-specific learning interval with the tester's achieved Frostbite score4334.67; it does not represent learning to MuZero's631378.53. AI above, known assessment cap difference5vs30min, prior general visual/motor skill difference. Source: agent-work/sources/games-memory/mnih2015-layout.txt lines388–400; MuZero v2 TableS1 and AppendixI.

MuZero full standard (not Reanalyze) recipe:20B environment frames, four-frame action repeat,1M updates×1024×five hypothetical recurrent steps; one initial representation per sample. Cached original actor search targets; no separate Reanalyze searches. Representation128 planes96², downsample48/24/12/6 with128/256 channels, then16 residual blocks; dynamics256 channels16blocks with18 action planes. Main actor5B roots×50 expansions. Need choose explicit evaluation allowance because final1000-episode protocol is reported but checkpoint count not. Do not silently omit evaluation or transfer EfficientZero reanalysis.

Maia next: primary paper and original repository being inspected for meaningful human move prediction versus actual play and reported timing.
