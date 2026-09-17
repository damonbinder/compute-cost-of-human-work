#!/usr/bin/env python3
"""Attention shape per model: full-attention layer count L and query width d_attn.

d_attn is n_query_heads * d_head, which is the width that enters the attention
FLOP count. It equals d_model for Llama-style models and does not in general:
gpt-oss-120b is 2880 wide with 64 heads of 64, and DeepSeek-V3's MLA carries a
128 * 160 = 20480 effective width against a 7168 model width.

L counts only layers whose attention cost grows with context. Sliding-window,
banded and linear-attention layers are excluded: their per-position cost is
bounded by the window or by the recurrent state.

DISCLOSED holds models whose config is public; everything else is bracketed from
the active-parameter prior by a dense-transformer shape, see shape_from_active.

Dependencies: Python 3.9+ standard library only.
"""

# model_id -> (L_full_attention, d_attn). Sources are tabulated in
# research/attention-correction.md#model-architectures.
DISCLOSED = {
    # Llama 2 family and continued-pretraining derivatives
    "llama-2-70b": (80, 8192),
    "llama-2-70b-chat": (80, 8192),
    "latxa-70b-v1.1": (80, 8192),
    "swallow-70b-base": (80, 8192),
    "llama-2-13b": (40, 5120),
    "latxa-13b-v1.1": (40, 5120),
    "acegpt-13b-base": (40, 5120),
    "llammas-base-7b": (32, 4096),
    "acegpt-7b-base": (32, 4096),
    "swallow-7b-base": (32, 4096),
    # Llama 3 family and fine-tunes
    "llama-3-8b-instruct": (32, 4096),
    "llama-3.1-8b-instruct": (32, 4096),
    "llama-3-70b-instruct": (80, 8192),
    "llama-3.1-70b-instruct": (80, 8192),
    "llama-3.3-70b-instruct": (80, 8192),
    "llama-3.2-90b-vision-instruct": (80, 8192),
    "deepseek-r1-distill-llama-70b": (80, 8192),
    "llama-3.1-tulu-3-70b-dpo": (80, 8192),
    "hermes-2-theta-llama-3-70b": (80, 8192),
    "llama-3.1-405b-instruct": (126, 16384),
    "llama-3.1-405b-base": (126, 16384),
    "llama-3.2-1b-instruct": (16, 2048),
    "llama-3.2-3b-instruct": (28, 3072),
    # Llama 4: chunked attention on three layers in four, one global in four
    "llama-4-scout": (12, 5120),
    "llama-4-maverick": (12, 5120),
    # Code Llama
    "code-llama-7b-base": (32, 4096),
    "code-llama-7b-kexer": (32, 4096),
    "code-llama-34b-base": (48, 8192),
    # Qwen
    "qwen2-72b-instruct": (80, 8192),
    "qwen2.5-72b-instruct": (80, 8192),
    "qwen2.5-32b-instruct": (64, 5120),
    "qwen2.5-7b-instruct": (28, 3584),
    "qwen2.5-math-1.5b-instruct": (28, 1536),
    "eurus-2-7b-prime": (28, 3584),
    "qwq-32b": (64, 5120),
    "qwq-plus": (64, 5120),
    "deepseek-r1-distill-qwen-32b": (64, 5120),
    "qwen1.5-32b-chat": (64, 5120),
    "qwen1.5-72b-chat": (80, 8192),
    "qwen3-235b-a22b-thinking-2507": (94, 8192),
    "qwen3-235b-a22b-instruct-2507": (94, 8192),
    # DeepSeek: MLA prefill width 128 heads * (192 qk + 128 v) / 2
    "deepseek-v3": (61, 20480),
    "deepseek-v3-0324": (61, 20480),
    "deepseek-v3.2": (61, 20480),
    "deepseek-r1": (61, 20480),
    "deepseek-r1-0528": (61, 20480),
    "deepseek-prover-v2-671b": (61, 20480),
    "deepseek-llm-67b-chat": (95, 8192),
    # Mistral
    "mistral-7b-instruct-v0.3": (32, 4096),
    "open-mistral-7b": (32, 4096),
    "mistral-nemo-2407": (40, 4096),
    "mistral-small-2501": (40, 4096),
    "mistral-small-2503": (40, 4096),
    "mistral-large-2402": (88, 12288),
    "mistral-large-2407": (88, 12288),
    "mistral-large-2411": (88, 12288),
    "ministral-8b-2410": (36, 4096),
    "mixtral-8x7b-instruct-v0.1": (32, 4096),
    "mixtral-8x22b-instruct-v0.1": (56, 6144),
    "wizardlm-2-8x22b": (56, 6144),
    # Gemma: alternating or 5:1 local/global, only global layers counted
    "gemma-2-9b-it": (21, 4096),
    "gemma-2-27b-it": (23, 4096),
    "gemma-3-27b-it": (10, 4096),
    # Microsoft
    "phi-4": (40, 5120),
    "phi-3-medium-128k-instruct": (40, 5120),
    # Others with public configs
    "dbrx-instruct": (40, 6144),
    "yi-1.5-34b-chat": (60, 7168),
    "yi-34b-chat": (60, 7168),
    "gpt-oss-120b": (18, 4096),
    "gpt-oss-20b": (12, 4096),
    "kimi-k2-instruct": (61, 10240),
    "kimi-k2.5": (61, 10240),
    "kimi-k2.6": (61, 10240),
    "kimi-k3": (24, 7168),
    "glm-4.7": (92, 12288),
    "minerva-62b": (64, 8192),
    "palm-540b-original": (118, 12288),
    "gpt-3-davinci-175b": (96, 12288),
    "text-davinci-002": (96, 12288),
    "implicit-cot-gpt2-mult4": (12, 768),
    "implicit-cot-gpt2-mult5": (12, 768),
    "implicit-cot-gpt2-mult7": (12, 768),
    "implicit-cot-gpt2-mult9": (12, 768),
    "implicit-cot-gpt2-mult11": (12, 768),
    "implicit-cot-gpt2-gsm8k-small": (12, 768),
    "implicit-cot-gpt2-gsm8k-medium": (24, 1024),
    "roberta-base": (12, 768),
}

# Models with a token coefficient but no attention: recurrent architectures.
NO_ATTENTION = {"gulordava-english-lstm-650"}


# Share of the dense bracket's layers that still run full attention, by family.
# The dense rule reproduces disclosed dense decoders to within 3% and was fitted
# to them, so it stands for the small academic models. For a closed frontier
# model it is an upper bound: every frontier architecture disclosed since March
# 2025 moves some layers to a local window or a linear state, and the multiplier
# is taken on the layer count rather than the width because that is the
# mechanism each of them uses. The evidence per family is tabulated in
# research/attention-correction.md#model-architectures.
FAMILY_LAYER_SHARE = {
    "openai": 0.65,
    "anthropic": 0.70,
    "google": 0.25,
    "xai": 1.00,
    "other_closed": 0.70,
    "dense": 1.00,
}

# company -> family. Anything not listed keeps the plain dense rule.
FAMILY_BY_COMPANY = {
    "OpenAI": "openai",
    "GitHub / OpenAI": "openai",
    "Anthropic": "anthropic",
    "Google DeepMind": "google",
    "Google": "google",
    "xAI": "xai",
    "Z.ai": "other_closed",
    "Alibaba": "other_closed",
    "MiniMax": "other_closed",
    "DeepSeek": "other_closed",
    "Meta": "other_closed",
    "Mistral AI": "other_closed",
    "Reka AI": "other_closed",
    "Thinking Machines": "other_closed",
    "MBZUAI Institute of Foundation Models": "other_closed",
    "NVIDIA": "other_closed",
}

# Companies whose estimated models are small dense research systems, where the
# frontier-family argument does not apply and the dense rule is accurate.
DENSE_COMPANIES = {
    "University of Oslo, Language Technology Group",
    "University of Illinois Urbana-Champaign",
    "Facebook",
    "Google Research",
    "Shanghai Jiao Tong University and Suzhou Laboratory",
}


def family_for(company):
    if company in DENSE_COMPANIES:
        return "dense"
    return FAMILY_BY_COMPANY.get(company, "other_closed")


def shape_from_active(active, family="dense"):
    """Attention shape consistent with an active-parameter prior.

    A dense decoder has about 12 * L * d^2 non-embedding parameters, and large
    models sit near an aspect ratio d = 128 * L (GPT-3 96/12288, Llama 3.1 70B
    80/8192, Llama 3.1 405B 126/16384). Solving the two together gives
    L_dense = (N / 196608)^(1/3) and d_attn = 128 * L_dense. The full-attention
    layer count is then the family's share of L_dense; the width is unchanged,
    because a local-attention interleave removes layers from the context-growing
    count and leaves the query width where it is.
    """
    dense = max(8, int(round((active / 196608.0) ** (1.0 / 3.0))))
    share = FAMILY_LAYER_SHARE.get(family, 1.0)
    layers = max(1, int(round(dense * share)))
    return layers, 128 * dense


def attention_shape(model_id, active, company=None):
    """(layers, width, basis) for a model."""
    if model_id in NO_ATTENTION:
        return None
    if model_id in DISCLOSED:
        return DISCLOSED[model_id] + ("reported",)
    if active is None:
        return None
    return shape_from_active(active, family_for(company)) + ("estimated",)
