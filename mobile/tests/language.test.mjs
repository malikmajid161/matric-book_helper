import test from 'node:test';
import assert from 'node:assert/strict';
import {detectLanguage,retrievalText} from '../src/language.ts';
import {resolveSavedExercise} from '../src/exercises.ts';

test('Roman Urdu detection is conservative and respects explicit English',()=>{
  assert.equal(detectLanguage('heat kya hai'),'roman-urdu');
  assert.equal(detectLanguage('ex1.1 samjhao'),'roman-urdu');
  assert.equal(detectLanguage('What is the main cause?'),'english');
  assert.equal(detectLanguage('ex1.1 roman urdu explain in English'),'english');
});
test('retrieval retains textbook terms and maps literal Roman Urdu vocabulary',()=>{
  assert.equal(retrievalText('heat kya hai'),'heat');
  assert.equal(retrievalText('garmi kya hai'),'heat');
  assert.equal(retrievalText('roshni aur awaz ka farq'),'light sound farq');
  assert.equal(retrievalText('internal energy samjhao'),'internal energy');
  assert.equal(retrievalText('mujhe batao'),'mujhe batao');
});
test('Roman Urdu questions receive the same simple English saved explanation',()=>{
  const item={id:'a',exercise:'1.1',question_number:1,part:'i',text:'Simplify i^5.',page_number:6,solution_status:'checked',solution:'1. Use i⁴ = 1.\n**Final answer:** i',solution_roman:'1. i⁴ = 1 ki qeemat rakhein.\n**Aakhri jawab:** i'};
  const bundle={id:'mathematics',chapters:[{number:1,title:'Complex Numbers',start_page:3,end_page:23,exercises:[item]}]};
  const english=resolveSavedExercise('ex1.1 q1 solution',bundle);
  const roman=resolveSavedExercise('ex1.1 q1 ka hal samjhao',bundle);
  assert.ok(english.supported&&roman.supported);
  assert.match(roman.answer,/## Question 1/);assert.match(roman.answer,/Final answer/);
  assert.equal(roman.answer,english.answer);
  assert.match(english.answer,/Final answer/);assert.deepEqual(roman.sources,english.sources);
  assert.match(roman.answer,/Simplify i\^5/);
});
