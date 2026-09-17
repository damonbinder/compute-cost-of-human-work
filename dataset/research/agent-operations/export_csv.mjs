// Values are authored through the spreadsheet library. CSV preserves the schema
// without adding workbook presentation or serializing dates as Excel numbers.
import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook} from '@oai/artifact-tool';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw new Error('Usage: export_csv.mjs MATRICES_JSON OUTPUT_DIR');
const matrices=JSON.parse(await fs.readFile(input,'utf8'));
const inspections=[];
for(const [name,matrix] of Object.entries(matrices)){
  const wb=Workbook.create();const sheet=wb.worksheets.add(name);
  sheet.getRangeByIndexes(0,0,matrix.length,matrix[0].length).values=matrix;
  wb.recalculate();
  const actual=sheet.getRangeByIndexes(0,0,matrix.length,matrix[0].length).values;
  if(JSON.stringify(actual)!==JSON.stringify(matrix))throw new Error(name+' values changed');
  inspections.push(await wb.inspect({kind:'region',sheetId:name,range:'A1:F4',maxChars:2000}));
  // The supplied public API has CSV import, but no documented CSV export.
  // Serialize the verified values using RFC4180 quoting, retaining blank cells.
  const csv=actual.map(row=>row.map(v=>{const s=v==null?'':String(v);return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;}).join(',')).join('\r\n')+'\r\n';
  await fs.writeFile(path.join(output,name+'.csv'),csv);
}
await fs.writeFile(path.join(output,'research','csv-inspection.json'),JSON.stringify(inspections,null,2)+'\n');
