// Read JSX syntax without executing the application or interpreting document text.
import ts from '../../frontend/node_modules/typescript/lib/typescript.js';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const result=[];
for(const filename of fs.readdirSync(path.join(root,'frontend/src')).filter(n=>n.endsWith('.tsx')).sort()) {
  const text=fs.readFileSync(path.join(root,'frontend/src',filename),'utf8');
  const source=ts.createSourceFile(filename,text,ts.ScriptTarget.Latest,true,ts.ScriptKind.TSX);
  const controls=[],labels=[];
  function visit(node){
    if(ts.isJsxElement(node)&&node.openingElement.tagName.getText(source)==='label')labels.push({line:source.getLineAndCharacterOfPosition(node.getStart()).line+1,syntax:node.getText(source).slice(0,1200)});
    if(ts.isJsxOpeningElement(node)||ts.isJsxSelfClosingElement(node)){
      const kind=node.tagName.getText(source);
      if(['input','select','textarea'].includes(kind))controls.push({line:source.getLineAndCharacterOfPosition(node.getStart()).line+1,kind,attributes:node.attributes.properties.map(p=>p.getText(source))});
    }
    ts.forEachChild(node,visit);
  }
  visit(source);if(controls.length)result.push({file:`frontend/src/${filename}`,controls,labels});
}
fs.writeFileSync(path.join(root,'docs/handbook/eingabeinventar_ui.json'),JSON.stringify({schema:'ims.ui-input-syntax-inventory.v1',date:'2026-10-06',method:'TypeScript AST; each control syntax once, dynamic loops represented by their source syntax. This is not a model-field validator.',components:result},null,2)+'\n');
process.stdout.write(`${result.length} components; ${result.reduce((n,r)=>n+r.controls.length,0)} control declarations\n`);
