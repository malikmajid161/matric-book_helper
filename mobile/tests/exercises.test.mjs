import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveSavedExercise} from '../src/exercises.ts';

const bundle={id:'mathematics',chapters:[{number:1,title:'Complex Numbers',start_page:3,end_page:23,exercises:[
  {id:'a',exercise:'1.1',question_number:1,part:'i',text:'Simplify i⁵.',page_number:6,solution_status:'checked',solution:'1. Use i⁴ = 1.\n2. Therefore i⁵ = i.'},
  {id:'b',exercise:'1.1',question_number:2,part:'i',text:'Write 2 + √(-4) in terms of i.',page_number:6,solution_status:'checked',solution:'2 + 2i.'},
]}]};
test('informal exercise solutions work without internet or native dependencies',()=>{
  for(const query of ['ex 1.1 soltion','excersise 1.1','excercise1.1'])assert.match(resolveSavedExercise(query,bundle).answer,/Therefore i⁵ = i/);
  const answer=resolveSavedExercise('exercise1.1 q2',bundle);
  assert.ok(answer.supported);assert.match(answer.answer,/2 \+ 2i/);assert.doesNotMatch(answer.answer,/Simplify/);
  assert.equal(answer.sources[0].page_number,6);assert.equal(answer.sources[0].citation,1);
});
test('question list excludes solutions, unknown and chapter mismatches do not invent them',()=>{
  const answer=resolveSavedExercise('give me all q of ex 1.1',bundle);
  assert.ok(answer.supported);assert.doesNotMatch(answer.answer,/Therefore/);
  assert.equal(resolveSavedExercise('ex1.1',bundle,2).supported,false);
  assert.equal(resolveSavedExercise('ex1.1 q3',bundle).supported,false);
  assert.equal(resolveSavedExercise('what is energy?',bundle),null);
  assert.equal(resolveSavedExercise('ex1.1 or ex1.2',bundle).supported,false);
});
test('draft solutions are not shown as verified',()=>{
  const copy=structuredClone(bundle);copy.chapters[0].exercises[0].solution_status='draft';
  const answer=resolveSavedExercise('ex1.1 q1 solution',copy);
  assert.equal(answer.supported,false);assert.match(answer.answer,/awaiting checking/);assert.doesNotMatch(answer.answer,/Therefore/);
});
