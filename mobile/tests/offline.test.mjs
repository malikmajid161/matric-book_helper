import test from 'node:test';
import assert from 'node:assert/strict';
import {queryVector,rankVectors} from '../src/vectorMath.ts';
import {answerCards} from '../src/answerCards.ts';

const model={model:'lsa-tfidf-1',dimensions:2,vocabulary:['energy','electrolysis'],idf:[1,1],projection:[[1,0],[0,1]]};
test('offline query and cosine search preserve chapter and page citations',()=>{
  const vector=queryVector(model,'Explain energy');
  const documents=[{id:'a',text:'Energy',chapter_number:14,chapter_title:'Energy',page_number:6,vector:[1,0]},{id:'b',text:'Current',chapter_number:15,chapter_title:'Electricity',page_number:28,vector:[0,1]}];
  assert.deepEqual(vector,[1,0]);
  assert.equal(rankVectors(documents,vector)[0].page_number,6);
  assert.deepEqual(rankVectors(documents,vector,15),[]);
  assert.equal(queryVector(model,'chlorophyll'),null);
});
test('study cards keep citations and numbered solution steps intact',()=>{
  const cards=answerCards('## Short answer\nEnergy [1].\n\n## Solve step by step\n1. Use the formula [2].\n2. Substitute.');
  assert.equal(cards.length,2);assert.equal(cards[0].title,'Short answer');
  assert.ok(cards[0].body.includes('[1]'));assert.ok(cards[1].body.includes('2. Substitute.'));
});
