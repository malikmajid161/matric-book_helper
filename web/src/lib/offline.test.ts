import {expect, test} from 'vitest';
import {findPassages} from './offline';
import type {Bundle} from './types';
const book: Bundle = {id:'physics',title:'Physics',edition:'Fixture',version:'fixture',sha256:'',chapters:[{number:12,title:'Waves',start_page:1,topics:[],exercises:[],pages:[{page_number:1,text:'A wave transfers energy through a medium. Frequency is measured in hertz.'}]},{number:13,title:'Sound',start_page:2,topics:[],exercises:[],pages:[{page_number:2,text:'Sound waves are longitudinal waves. Sound travels through a medium.'}]}]};
test('local evidence preserves its page and does not answer unrelated questions', () => {
  expect(findPassages(book,'frequency hertz')[0].page_number).toBe(1);
  expect(findPassages(book,'photosynthesis chlorophyll')).toEqual([]);
  expect(findPassages(book,'sound',12)).toEqual([]);
});
