# Remaining source identity investigations

## reas-epoch-gpqa-qwq32b

The task lead labels this QwQ-32B (qwq-plus), but the original scatter_data.csv identifies **qwq-plus**, GPQA score 0.6540404040404041, output mean 8802.373737373737. Its listed April 8 date is not accepted as original release evidence. The [original open QwQ release](https://qwenlm.github.io/blog/qwq-32b/) dated March 6 reports 32B parameters and demonstrates API model=qwq-32b. [Alibaba's qwq-plus model documentation](https://help.aliyun.com/zh/model-studio/qwq-plus) instead calls it an enhanced QwQ reasoning model based on Qwen2.5, without a disclosed parameter count. [Alibaba's March release recap](https://developer.aliyun.com/article/1659474) lists qwq-plus, qwq-plus-latest and qwq-plus-2025-03-05 as March additions. Thus open 32B size and the output-table April 8 date cannot be silently assigned to this hosted alias. The incorporated observation uses a separately justified Qwen-family size estimate, as summarized below.

## Hermes and WizardLM

Incorporated with the additional-model collection. Hermes original model/config/tokenizer and contemporary release account support a dense 70B merge; repository creation is not release. WizardLM original launch is accessible even though original model hosting was removed; pinned preserved config/tokenizer support the Mixtral backbone. See [epoch-additional-models.md](epoch-additional-models.md) for calculations and limitations.

Resolution: QwQ-Plus is incorporated with its true hosted alias, an explicitly estimated 32B family coefficient and original March 6 Lingma availability evidence. This does not establish equality with open QwQ-32B. See epoch-reasoning-families.md.
