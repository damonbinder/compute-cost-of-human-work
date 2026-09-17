#!/usr/bin/env python3
"""Compute the HourVideo / Gemini 1.5 Pro rows.

Reads the retained source figures, applies the point-specific assumptions
recorded in ASSUMPTIONS below, and writes a calculations JSON.

Every reported number enters through the sources file; nothing reported is
written here. Everything in ASSUMPTIONS is ours, not the source's.

Dependencies: Python 3.8+ standard library only.

Usage:
    python3 compute_hourvideo.py \
        --figures agent-work/sources/hourvideo/hourvideo-reported-figures.json \
        --out calculations.json

Paths are explicit; the script does not guess a repository layout and does not
modify the file it reads.
"""

import argparse
import json
import math
import os


# ---------------------------------------------------------------------------
# Point-specific assumptions. These are ours. Their basis is argued in
# research/hourvideo.md; the bands are carried into the scenario tables below.
# ---------------------------------------------------------------------------
ASSUMPTIONS = {
    "flops_per_position": 2.0e11,
    "flops_per_position_basis": (
        "2 x 100e9 active parameters, the dataset's shared Gemini Pro frontier prior, "
        "applied to text, video and audio positions alike"
    ),
    "active_parameters_band": [30e9, 300e9],

    # Visual encoder. The ImageNet row this study follows for the tokens convention
    # keeps the encoder term inside compute_flops (2 * encoder_params * patches), so
    # this row does too. Gemini's encoder is undisclosed; 2B parameters and 14-pixel
    # patches are transferred from that row's OpenCLIP ViT-bigG/14 reference, applied
    # to the 512x384 frame actually uploaded. Added in Revision 2.
    "encoder_parameters": 2.0e9,
    "encoder_patch_pixels": 14,
    "frame_pixels": [512, 384],
    "encoder_patches_per_frame_scenarios": {
        "resized_to_the_258_token_grid": 256,
        "16_pixel_patches": 768,
    },

    # Donor batch composition. How a participant's 27 questions were assigned across
    # the ten videos is not published. Two readings, both carried. Added in Revision 2.
    "donor_batch_composition": "video_blocked",

    # Text-token estimate, per research/hourvideo.md#text-tokens.
    "chars_per_token": 4.0,
    "prompt_file_yaml_overhead_chars": 15,
    "mcq_text_chars": 800,          # question + five options + formatting
    "mcq_text_chars_band": [600, 1200],
    "output_tokens_per_mcq": 110,   # YOUR_ANSWER string + JUSTIFICATION + JSON scaffolding
    "output_tokens_per_mcq_band": [60, 200],

    # Bracketing decoder shapes for the omitted cached-context attention term.
    # Gemini's architecture is not disclosed; these bracket a frontier decoder
    # of roughly 100B active parameters, as research/portal-astra.md does.
    "attention_shapes": [
        {"label": "L=64, d=8192", "layers": 64, "d_model": 8192},
        {"label": "L=80, d=10240", "layers": 80, "d_model": 10240},
        {"label": "L=96, d=12288", "layers": 96, "d_model": 12288},
    ],
}


def build(fig):
    hv = fig["hourvideo_paper"]
    tab3 = hv["table_3_ablation"]
    repo = fig["hourvideo_repo"]
    tok = fig["gemini_video_tokenization"]
    donor = fig["one_hour_walk_vqa_donor"]
    price = fig["gemini_15_pricing"]
    A = ASSUMPTIONS

    out = {"assumptions": A, "reported_inputs_echo": {
        "table_3": tab3,
        "human_experts": hv["human_experts"],
        "donor": {k: v for k, v in donor.items() if not k.startswith("_")},
    }}

    # -- the ablation set -----------------------------------------------------
    videos = tab3["videos"]
    mcqs = tab3["mcqs"]
    total_video_s = tab3["hours_of_video"] * 3600.0
    mean_video_s = total_video_s / videos
    mcqs_per_video = mcqs / videos

    out["ablation_set"] = {
        "videos": videos,
        "mcqs": mcqs,
        "total_video_seconds": total_video_s,
        "mean_video_seconds": mean_video_s,
        "mean_video_minutes": mean_video_s / 60.0,
        "mcqs_per_video": mcqs_per_video,
    }

    # -- cost cross-check: is Table 3's token column a billed input count? ----
    rate = price["above_128k_input_usd_per_million_before_2024_10_01"]
    out["cost_cross_check"] = {
        "assumed_unit_price_usd_per_million": rate,
        "note": ("Table 3's token column times this rate reproduces both published "
                 "costs, so the column is the billed input-token total and the "
                 "authors priced all of it at the above-128K input rate"),
    }
    for mode in ("task_level", "individual"):
        t = tab3[mode]["total_tokens"]
        implied = t * rate / 1e6
        out["cost_cross_check"][mode] = {
            "total_tokens": t,
            "published_cost_usd": tab3[mode]["evaluation_cost_usd"],
            "implied_cost_usd": implied,
            "rounds_to_published": round(implied) == tab3[mode]["evaluation_cost_usd"],
            "implied_usd_per_million": tab3[mode]["evaluation_cost_usd"] / t * 1e6,
        }

    # -- tokenizer cross-check ------------------------------------------------
    # The uploaded MP4 is silent (cv2.VideoWriter carries no audio stream), so
    # the documented audio term does not apply; the rate is one frame per second
    # of timeline at the high-media-resolution frame cost.
    rate_per_s = tok["tokens_per_frame_high"] * tok["frames_per_second_sampled"]
    audio_applies = repo["audio_track_written"]
    if audio_applies:
        rate_per_s += tok["audio_tokens_per_second"]
    full_pass_positions = rate_per_s * mean_video_s

    ind_tokens = tab3["individual"]["total_tokens"]
    tl_tokens = tab3["task_level"]["total_tokens"]
    observed_per_s_per_pass = ind_tokens / (mcqs * mean_video_s)

    out["tokenizer_cross_check"] = {
        "documented_tokens_per_second_of_video": rate_per_s,
        "audio_term_applied": audio_applies,
        "audio_note": repo["_audio_note"],
        "full_pass_positions_at_mean_duration": full_pass_positions,
        "individual_mode_is_one_pass_per_mcq": True,
        "observed_tokens_per_second_of_video_per_pass": observed_per_s_per_pass,
        "excess_over_documented": observed_per_s_per_pass / rate_per_s,
        "excess_note": (
            "Computed against the plain mean video duration. Calls are weighted by "
            "questions per video, so if question count rises with video length the "
            "question-weighted mean duration exceeds the plain mean and absorbs the "
            "excess; a question-weighted mean of "
            f"{ind_tokens / mcqs / rate_per_s:.0f} s reconciles it exactly. "
            "Refusal retries would push the same way."
        ),
        "question_weighted_mean_duration_implied_s": ind_tokens / mcqs / rate_per_s,
        "full_video_equivalent_passes_per_video": {
            "task_level": (tl_tokens / videos) / full_pass_positions,
            "individual": (ind_tokens / videos) / full_pass_positions,
        },
        "task_level_to_individual_token_ratio": tl_tokens / ind_tokens,
        "implied_calls_per_video_task_level_naive": (tl_tokens / ind_tokens) * mcqs_per_video,
    }

    # -- text tokens ----------------------------------------------------------
    prompt_chars = repo["prompt_file"]["size_bytes"] - A["prompt_file_yaml_overhead_chars"]
    prompt_tokens = prompt_chars / A["chars_per_token"]
    mcq_tokens = A["mcq_text_chars"] / A["chars_per_token"]
    calls = {
        "task_level": (tl_tokens / ind_tokens) * mcqs_per_video,
        "individual": mcqs_per_video,
    }
    out["text_tokens"] = {
        "prompt_file_bytes": repo["prompt_file"]["size_bytes"],
        "instruction_tokens_per_call": prompt_tokens,
        "mcq_text_tokens_per_mcq": mcq_tokens,
        "output_tokens_per_mcq": A["output_tokens_per_mcq"],
        "calls_per_video": calls,
    }

    # -- the two rows ---------------------------------------------------------
    out["rows"] = {}
    for mode, point_id in (("task_level", "perc-hourvideo-gemini15pro-tasklevel"),
                           ("individual", "perc-hourvideo-gemini15pro-individual")):
        billed_input_per_video = tab3[mode]["total_tokens"] / videos
        input_text = calls[mode] * prompt_tokens + mcqs_per_video * mcq_tokens
        output_text = mcqs_per_video * A["output_tokens_per_mcq"]
        video_positions = billed_input_per_video - input_text
        processed = billed_input_per_video + output_text
        backbone_flops = processed * A["flops_per_position"]

        # Visual encoder, per the ImageNet precedent. One frame is charged 258 backbone
        # positions, so the frame count is the video-position count divided by that rate.
        frames = video_positions / rate_per_s * tok["frames_per_second_sampled"]
        patches = (A["frame_pixels"][0] * A["frame_pixels"][1]) / A["encoder_patch_pixels"] ** 2
        encoder_flops = frames * 2.0 * A["encoder_parameters"] * patches
        flops = backbone_flops + encoder_flops

        row = {
            "point_id": point_id,
            "accuracy_percent": tab3[mode]["accuracy_percent"],
            "backbone_flops": backbone_flops,
            "frames_charged_per_video": frames,
            "encoder_patches_per_frame": patches,
            "encoder_flops": encoder_flops,
            "encoder_share_of_total": encoder_flops / flops,
            "billed_input_positions_per_video": billed_input_per_video,
            "input_text_tokens": input_text,
            "output_text_tokens": output_text,
            "csv_tokens_text_only": input_text + output_text,
            "video_positions": video_positions,
            "video_share_of_positions": video_positions / billed_input_per_video,
            "total_processed_positions": processed,
            "compute_flops": flops,
            "compute_flops_per_mcq": flops / mcqs_per_video,
        }

        # cached-context attention, one causal prefill per call at N positions
        n_ctx = full_pass_positions
        att = {}
        for shape in A["attention_shapes"]:
            coeff = 2.0 * shape["layers"] * shape["d_model"]
            total_att = coeff * billed_input_per_video * n_ctx
            att[shape["label"]] = {
                "layers": shape["layers"],
                "d_model": shape["d_model"],
                "context_positions_per_call": n_ctx,
                "attention_flops": total_att,
                "ratio_to_recorded": total_att / flops,
                "full_operation_count": total_att + flops,
                "full_over_recorded": (total_att + flops) / flops,
            }
        row["cached_context_attention"] = {
            "recipe": "4 * layers * d_model * N(N+1)/2 per causal prefill, approximated as 2 * layers * d_model * N^2 and summed over calls at fixed total positions",
            "note": "One-sided: the shared coefficient can only understate. An upper bound if Gemini 1.5's long-context mechanism is not dense attention.",
            "shapes": att,
        }

        lo, hi = A["active_parameters_band"]
        # The parameter prior scales the backbone only; the encoder carries its own
        # parameter count and does not move with it.
        row["scenarios"] = {
            "active_parameters_30B": backbone_flops * (2 * lo) / A["flops_per_position"] + encoder_flops,
            "active_parameters_300B": backbone_flops * (2 * hi) / A["flops_per_position"] + encoder_flops,
            "mcq_text_600_chars": (calls[mode] * prompt_tokens
                                   + mcqs_per_video * A["mcq_text_chars_band"][0] / A["chars_per_token"]
                                   + output_text),
            "mcq_text_1200_chars": (calls[mode] * prompt_tokens
                                    + mcqs_per_video * A["mcq_text_chars_band"][1] / A["chars_per_token"]
                                    + output_text),
            "per_mcq_work_unit_flops": flops / mcqs_per_video,
            "backbone_only_no_encoder": backbone_flops,
        }
        for label, pc in A["encoder_patches_per_frame_scenarios"].items():
            row["scenarios"]["encoder_" + label] = (
                backbone_flops + frames * 2.0 * A["encoder_parameters"] * pc)
        out["rows"][mode] = row

    # Appendix E upper scenario applies to the task-level protocol only.
    tl_usd_per_hour = tab3["task_level"]["evaluation_cost_usd"] / tab3["hours_of_video"]
    appx = hv["appendix_e_cost"]["usd_per_hour_of_video"]
    out["rows"]["task_level"]["scenarios"]["appendix_e_cost_upper"] = {
        "table_3_usd_per_hour_of_video": tl_usd_per_hour,
        "appendix_e_usd_per_hour_of_video": appx,
        "multiplier": appx / tl_usd_per_hour,
        "compute_flops": out["rows"]["task_level"]["compute_flops"] * appx / tl_usd_per_hour,
    }

    # -- human time -----------------------------------------------------------
    per_question_s = donor["mean_batch_seconds"] / donor["questions_per_participant_batch"]
    donor_attempts = donor["questions_total"] * donor["answers_per_question"]
    donor_batches = donor_attempts / donor["questions_per_participant_batch"]

    wt = fig["walking_tours_corpus"]
    donor_video_s = wt["videos"] * wt["mean_video_seconds"]
    donor_q_per_video = donor["questions_total"] / donor["videos"]

    # Transfer A: a rate per question.
    transfer_a = per_question_s * mcqs_per_video

    # Transfer B: a rate per second of video. How much video a 27-question batch puts
    # in front of a participant depends on how the batch was composed, which the donor
    # does not publish. Two readings.
    #
    # (i) Video-blocked: a batch is whole videos' worth of questions, so it spans
    #     27 / (70/10) = 3.857 videos. Equivalently, one full coverage of the
    #     70-question set costs (70/27) * 13800 s against the whole 58,800 s corpus.
    videos_per_batch_blocked = donor["questions_per_participant_batch"] / donor_q_per_video
    rate_blocked = donor["mean_batch_seconds"] / (videos_per_batch_blocked * wt["mean_video_seconds"])
    transfer_b_blocked = rate_blocked * mean_video_s

    # (ii) Randomly assigned: 27 of the 70 questions drawn at random touch
    #      sum_v [1 - C(N - n_v, k) / C(N, k)] videos in expectation.
    N = donor["questions_total"]
    k = donor["questions_per_participant_batch"]

    def expected_videos(counts):
        return sum(1.0 - math.comb(N - n, k) / math.comb(N, k) for n in counts)

    uniform_counts = [donor["questions_total"] // donor["videos"]] * donor["videos"]
    videos_per_batch_random = expected_videos(uniform_counts)
    # The split table shows the questions are not evenly spread; this vector is one
    # integer realisation of 11 over 3 validation videos and 59 over 7 test videos.
    split_counts = [4, 4, 3, 9, 9, 9, 8, 8, 8, 8]
    videos_per_batch_random_split = expected_videos(split_counts)
    rate_random = donor["mean_batch_seconds"] / (videos_per_batch_random * wt["mean_video_seconds"])
    transfer_b_random = rate_random * mean_video_s

    # DECISIONS.md: two defensible transfers, neither privileged, so the central is
    # their geometric mean. Transfer B uses the video-blocked reading, which treats the
    # donor most generously; the random reading is carried as one-sided residual
    # uncertainty on that leg (coordinator's ruling, Revision 2).
    central = (transfer_a * transfer_b_blocked) ** 0.5
    central_random_leg = (transfer_a * transfer_b_random) ** 0.5

    out["human_time"] = {
        "donor_seconds_per_question": per_question_s,
        "donor_contributing_attempts": donor_attempts,
        "donor_batches": donor_batches,
        "donor_accuracy_percent": donor["accuracy_percent"],
        "donor_questions_per_video": donor_q_per_video,
        "donor_corpus_video_seconds": donor_video_s,
        "donor_mean_video_seconds": wt["mean_video_seconds"],
        "donor_full_coverage_seconds": (N / k) * donor["mean_batch_seconds"],
        "batch_composition": {
            "video_blocked_videos_per_batch": videos_per_batch_blocked,
            "video_blocked_seconds_per_second_of_video": rate_blocked,
            "random_videos_per_batch_uniform_counts": videos_per_batch_random,
            "random_videos_per_batch_split_counts": videos_per_batch_random_split,
            "random_seconds_per_second_of_video": rate_random,
            "note": ("The donor publishes neither the assignment rule nor a per-video "
                     "question count. Both readings shorten transfer B relative to "
                     "transfer A, so the residual uncertainty is one-sided."),
        },
        "transfer_a_per_question_s": transfer_a,
        "transfer_b_per_second_of_video_s": transfer_b_blocked,
        "transfer_spread": transfer_a / transfer_b_blocked,
        "central_rule": "geometric mean of the two transfers, transfer B on the video-blocked reading",
        "central_per_video_question_set_s": central,
        "central_csv_value_s": round(central),
        "central_hours": central / 3600.0,
        "central_over_video_running_time": central / mean_video_s,
        "scenarios": {
            "per_question_rate_transfer_s": transfer_a,
            "per_question_rate_over_running_time": transfer_a / mean_video_s,
            "per_second_of_video_rate_video_blocked_s": transfer_b_blocked,
            "per_second_of_video_rate_video_blocked_over_running_time": transfer_b_blocked / mean_video_s,
            "per_second_of_video_rate_random_batches_s": transfer_b_random,
            "per_second_of_video_rate_random_batches_over_running_time": transfer_b_random / mean_video_s,
            "central_if_transfer_b_uses_random_batches_s": central_random_leg,
            "watch_once_floor_video_running_time_s": mean_video_s,
            "per_question_work_unit_s": per_question_s,
        },
    }

    # -- implied compute per human second, for the note's summary table -------
    out["summary"] = {}
    for mode in ("task_level", "individual"):
        f = out["rows"][mode]["compute_flops"]
        out["summary"][mode] = {
            "compute_flops": f,
            "human_time_s": central,
            "human_time_csv_s": round(central),
            "flops_per_human_second": f / central,
            "flops_per_human_second_at_csv_value": f / round(central),
            "flops_per_human_second_per_question_transfer": f / transfer_a,
            "flops_per_human_second_per_second_of_video_transfer": f / transfer_b_blocked,
            "flops_per_human_second_random_batch_central": f / central_random_leg,
            "accuracy_percent": tab3[mode]["accuracy_percent"],
            "human_accuracy_percent": hv["human_experts"]["accuracy_percent"],
        }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--figures", required=True,
                    help="path to agent-work/sources/hourvideo/hourvideo-reported-figures.json")
    ap.add_argument("--out", required=True, help="path to write calculations JSON")
    args = ap.parse_args()

    with open(args.figures) as fh:
        fig = json.load(fh)
    result = build(fig)
    result["_generated_by"] = "research/hourvideo/compute_hourvideo.py"
    result["_figures_source"] = os.path.basename(args.figures)

    with open(args.out, "w") as fh:
        json.dump(result, fh, indent=2)
        fh.write("\n")
    print("wrote", args.out)

    s = result["summary"]
    for mode in ("task_level", "individual"):
        r = s[mode]
        print(f"{mode:11s} compute {r['compute_flops']:.6e} FLOPs  "
              f"human {r['human_time_s']:.0f} s  "
              f"{r['flops_per_human_second']:.3e} FLOPs/human-second  "
              f"AI {r['accuracy_percent']}% vs human {r['human_accuracy_percent']}%")


if __name__ == "__main__":
    main()
