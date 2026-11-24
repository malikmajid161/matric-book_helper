import 'fake-indexeddb/auto';
import {webcrypto} from 'node:crypto';
import {beforeAll,expect,test} from 'vitest';
import {type ChapterPack,saveChapterPack,loadChapterPack,listChapterPacks,removeChapterPack} from './chapterStorage';

beforeAll(()=>{Object.defineProperty(globalThis,'crypto',{value:webcrypto,configurable:true});Object.defineProperty(globalThis,'navigator',{value:{storage:{persist:async()=>true}},configurable:true});});
async function fixture(id:string,number:number):Promise<ChapterPack>{const pdf=new Blob([`%PDF-${id}-${number}`]);const sha256=Buffer.from(await webcrypto.subtle.digest('SHA-256',await pdf.arrayBuffer())).toString('hex');return {pdf,bundle:{id,title:id,edition:'Fixture',version:'one',sha256,bytes:pdf.size,chapter_number:number,pdf_page_offset:2,chapters:[{number,title:'Energy',start_page:3,end_page:4,topics:[],exercises:[]}]}};}

test('same chapter number stays isolated between class 9 and class 10 books',async()=>{
  await saveChapterPack(await fixture('physics9',1));await saveChapterPack(await fixture('physics',1));
  expect(await (await loadChapterPack('physics9',1))?.pdf.text()).toBe('%PDF-physics9-1');
  expect(await (await loadChapterPack('physics',1))?.pdf.text()).toBe('%PDF-physics-1');
  expect((await listChapterPacks()).filter(pack=>['physics9','physics'].includes(pack.bundle.id))).toHaveLength(2);
});
test('removing one chapter preserves other chapters and subjects',async()=>{
  await saveChapterPack(await fixture('chemistry',14));await saveChapterPack(await fixture('chemistry',15));await saveChapterPack(await fixture('chemistry9',1));
  await removeChapterPack('chemistry',14);
  expect(await loadChapterPack('chemistry',14)).toBeUndefined();expect(await loadChapterPack('chemistry',15)).toBeDefined();expect(await loadChapterPack('chemistry9',1)).toBeDefined();
});
test('bad checksum cannot replace an existing valid chapter',async()=>{
  const valid=await fixture('mathematics',1);await saveChapterPack(valid);
  await expect(saveChapterPack({...valid,pdf:new Blob(['damaged'])})).rejects.toThrow('verification');
  expect(await (await loadChapterPack('mathematics',1))?.pdf.text()).toBe('%PDF-mathematics-1');
});
