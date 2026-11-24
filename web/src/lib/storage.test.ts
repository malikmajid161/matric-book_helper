import 'fake-indexeddb/auto';
import {webcrypto} from 'node:crypto';
import {beforeAll, expect, test} from 'vitest';
import {checksum, loadBook, removeBook, saveBook,saveAnswer,loadAnswer} from './storage';
import type {Bundle} from './types';
beforeAll(() => {Object.defineProperty(globalThis, 'crypto', {value: webcrypto}); Object.defineProperty(globalThis, 'navigator', {value: {storage: {persist: async () => true}}, configurable: true});});
test('download verifies, survives reload, and deletion requires download again', async () => {
  const pdf = new Blob(['%PDF-test-data']);
  const bundle: Bundle = {id: 'physics', title: 'Physics', edition: 'Fixture', version: 'test', sha256: await checksum(pdf), chapters: []};
  await saveBook(bundle, pdf);
  const cached = await loadBook('physics');
  expect(cached?.bundle.version).toBe('test');
  expect(await cached?.pdf.text()).toBe('%PDF-test-data');
  await removeBook('physics');
  expect(await loadBook('physics')).toBeUndefined();
});
test('corrupted downloads are not stored', async () => {
  const bundle: Bundle = {id: 'chemistry', title: 'Chemistry', edition: 'Fixture', version: 'test', sha256: 'bad', chapters: []};
  await expect(saveBook(bundle, new Blob(['corrupted']))).rejects.toThrow('verification');
  expect(await loadBook('chemistry')).toBeUndefined();
});
test('saved AI answers are scoped to the student and textbook version',async()=>{
 const bundle:Bundle={id:'chemistry',title:'Chemistry',edition:'Fixture',version:'one',sha256:'',chapters:[]};
 const answer={answer:'Energy [1]',supported:true,sources:[]};
 await saveAnswer('ayesha',bundle,'Internal energy',answer);
 expect(await loadAnswer('ayesha',bundle,'internal energy')).toEqual(answer);
 expect(await loadAnswer('huzaifa',bundle,'internal energy')).toBeUndefined();
 expect(await loadAnswer('ayesha',{...bundle,version:'two'},'internal energy')).toBeUndefined();
});
