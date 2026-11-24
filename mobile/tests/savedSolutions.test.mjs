import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveSavedQuestion} from '../src/savedSolutions.ts';

const question={id:'a',text:'14.1 What is internal energy?',page_number:8,solution_status:'checked',solution:'## Short answer\nIt is the total particle energy. [9]',solution_source_pages:[6]};
const bundle={id:'chemistry',chapters:[{number:14,title:'States of Matter',start_page:3,end_page:20,exercises:[question],pages:[{page_number:6,text:'Original textbook statement about energy.'},{page_number:8,text:'Original exercise page: What is internal energy?'}]}]};
test('exact prose matching ignores labels, case and harmless punctuation',()=>{
  for(const query of ['what is internal energy','14.1 WHAT IS INTERNAL ENERGY?','Question 14.1 What is internal energy?']){
    const result=resolveSavedQuestion(query,bundle);
    assert.ok(result?.supported);assert.match(result.answer,/total particle energy/);
    assert.equal(result.sources.length,2);assert.equal(result.sources[0].page_number,8);assert.equal(result.sources[1].page_number,6);
    assert.equal(result.sources[1].text,'Original textbook statement about energy.');
    assert.match(result.answer,/material.*\[2\]/);assert.doesNotMatch(result.answer,/\[9\]/);
  }
});
test('near matches, typos, unchecked and chapter mismatches return no fabricated answer',()=>{
  assert.equal(resolveSavedQuestion('what is external energy',bundle),null);
  assert.equal(resolveSavedQuestion('what is interal energy',bundle),null);
  assert.equal(resolveSavedQuestion('what is internal energy',bundle,15),null);
  const draft=structuredClone(bundle);draft.chapters[0].exercises[0].solution_status='draft';
  assert.equal(resolveSavedQuestion('what is internal energy',draft),null);
});
test('different signs, digits, powers and decimal values stay different',()=>{
  const copy=structuredClone(bundle);copy.chapters[0].exercises[0]={...question,text:'Solve x^2 + 2.5x = 3.',solution:'x = 1',solution_source_pages:[6]};
  assert.ok(resolveSavedQuestion('Solve x ^ 2 + 2.5x = 3',copy));
  for(const query of ['Solve x^2 - 2.5x = 3','Solve x^3 + 2.5x = 3','Solve x^2 + 25x = 3','Solve x^2 + 2.5x = 4'])assert.equal(resolveSavedQuestion(query,copy),null);
});
test('ambiguous duplicate answers or absent declared evidence return null',()=>{
  const copy=structuredClone(bundle);copy.chapters[0].exercises.push({...question,id:'b',solution:'A different answer.'});
  assert.equal(resolveSavedQuestion('what is internal energy',copy),null);
  const missing=structuredClone(bundle);missing.chapters[0].exercises[0].solution_source_pages=[7];
  assert.equal(resolveSavedQuestion('what is internal energy',missing),null);
});
test('factorial, ratio and coordinate punctuation remain mathematical symbols',()=>{
  for(const [text,changed] of [['Calculate 5!','Calculate 5'],['Simplify 1:2','Simplify 1 2'],['Use (1,2)','Use (1 2)']]){
    const copy=structuredClone(bundle);copy.chapters[0].exercises[0]={...question,text};
    assert.ok(resolveSavedQuestion(text,copy));assert.equal(resolveSavedQuestion(changed,copy),null);
  }
});
test('no explicit source list uses original question page, never generated text',()=>{
  const copy=structuredClone(bundle);delete copy.chapters[0].exercises[0].solution_source_pages;
  const result=resolveSavedQuestion('what is internal energy',copy);
  assert.equal(result.sources.length,1);assert.equal(result.sources[0].page_number,8);
  assert.equal(result.sources[0].text,'Original exercise page: What is internal energy?');
});
