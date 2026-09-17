import json
C=1024;T=820;D=1536;R=128;s=8
frame_weights={'first_conv':80*C*5,'three_res2_blocks':3*(2*C*C+7*(C//s)**2*3),'multi_layer_aggregation':3*C*D,'context_attention':3*D*R+R*D}
terms={k:2*v*T for k,v in frame_weights.items()}
terms['SE_dense']=3*2*(C*R+R*C)
terms['embedding_dense']=2*(2*D)*192
terms['SE_mean_and_gate']=6*C*T
terms['residual_and_Res2_sums']=(6*C+3*6*(C//s))*T
terms['BN_affine']=2*((C+3*(2*C+7*C//s))*T+2*D+192)
terms['pooling_softmax_context']=20*D*T+10*D
terms['SE_sigmoid']=3*4*C
terms['embedding_length_normalization']=4*192
terms['MFCC_front_end']=T*(2.5*512*9+2*80*257+2*80*80+400+4*257+80+2*80)
pair={k:2*v for k,v in terms.items()}
pair['cohort_cosines']=2*5994*2*192
pair['cohort_top1000_statistics_and_score']=2*6*1000+2*192+20
out={'channels':C,'frames_per_utterance':T,'seconds_per_utterance_proxy':8.2,'frame_weights':frame_weights,'inference_weight_count_excluding_bias_and_BN':sum(frame_weights.values())+3*(C*R+R*C)+2*D*192,'per_utterance_flops':terms,'pair_flops':pair,'total_flops':sum(pair.values()),'human_seconds':2*8.2+2}
print(json.dumps(out,indent=2))
