// Node.js built-ins only. Execute only the two hash-pinned, inspected pure functions.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const vm = require('vm');
const [sourceDir, outputDir] = process.argv.slice(2);
if (!sourceDir || !outputDir) throw new Error('Usage: node recompute.js SOURCES_DIRECTORY NEW_OUTPUT_DIRECTORY');
const resolvedSource = fs.realpathSync(sourceDir);
const resolvedOutput = path.resolve(outputDir);
const relativeOutput = path.relative(resolvedSource, resolvedOutput);
if (!relativeOutput || (!relativeOutput.startsWith('..' + path.sep) && relativeOutput !== '..' && !path.isAbsolute(relativeOutput))) throw new Error('Output must be outside sources');
if (fs.existsSync(outputDir)) throw new Error('Output directory must be new');
const bytes = fs.readFileSync(path.join(sourceDir, 'evals-Clean_markdown__Medium_-2025-07-24.json'));
if (crypto.createHash('sha256').update(bytes).digest('hex') !== '8bbebea4dd246aaa93e2757a3392c2c62e71afc4ef48d55b6e624682f29552da') throw new Error('Unexpected source hash');
const data = JSON.parse(bytes);
function unwrap(value) {
  const begin = value.indexOf('```');
  const end = value.lastIndexOf('```');
  if (begin < 0 || end === begin) throw new Error('Missing code fence');
  return value.slice(value.indexOf('\n', begin) + 1, end).replace(/\n$/, '');
}
const get = name => unwrap(data.contexts.find(c => c.content.startsWith(name + '\n')).content);
const input = get('sample-input.md');
const expected = get('expected-output.md');
const results = [];
for (const [model, coefficient] of [['claude-sonnet-4-20250514',200000000000],['claude-opus-4-20250514',360000000000]]) {
  const records = data.evals.filter(e => e.model === model);
  if (records.length !== 1) throw new Error('Unexpected run count');
  const record = records[0];
  const original = unwrap(record.response);
  const code = original.replace('export function cleanMarkdown(markdown: string): string', 'function cleanMarkdown(markdown)');
  if (code === original) throw new Error('Unexpected declaration');
  const actual = vm.runInNewContext(code + '\ncleanMarkdown(input)', {input}, {timeout:1000});
  const u = record.usage;
  if (u.promptTokens + u.completionTokens !== u.totalTokens || u.thoughtsTokens !== 0) throw new Error('Unexpected token accounting');
  results.push({model,run_id:record.id,input_tokens:u.promptTokens,output_tokens:u.completionTokens,tokens:u.totalTokens,flops_per_token:coefficient,compute_flops:u.totalTokens*coefficient,human_time:600,passes:actual.trim()===expected.trim(),expected_length:expected.trim().length,actual_length:actual.trim().length,actual_output:actual});
}
fs.mkdirSync(outputDir, {recursive:true});
fs.writeFileSync(path.join(outputDir,'sample-input.md'),input);
fs.writeFileSync(path.join(outputDir,'expected-output.md'),expected);
fs.writeFileSync(path.join(outputDir,'results.json'),JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results.map(({model,tokens,compute_flops,passes})=>({model,tokens,compute_flops,passes})),null,2));
