// Optional regeneration of standard BPE ranks from original Anthropic compressed vocabulary.
// Requires npm package tiktoken. Arguments: original-json new-output-file.
const fs=require('fs'),path=require('path'),{Tiktoken}=require('tiktoken/lite');
if(process.argv.length!==4)throw Error('Provide original JSON and a new output file');
const src=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
if(fs.existsSync(out)||out===src)throw Error('Output must be new');
const c=JSON.parse(fs.readFileSync(src)),t=new Tiktoken(c.bpe_ranks,c.special_tokens,c.pat_str),a=[];
for(let i=5;i<c.explicit_n_vocab;i++)a.push(Buffer.from(t.decode(new Uint32Array([i]))).toString('base64')+' '+i);
fs.writeFileSync(out,a.join('\n')+'\n',{flag:'wx'});t.free();
