import {openDB} from 'idb';
import type {Bundle} from './types';

export type ChapterBundle = Bundle & {chapter_number:number;pdf_page_offset:number;bytes:number};
export type ChapterPack = {bundle:ChapterBundle;pdf:Blob;savedAt?:number};
const database=()=>openDB('ptb-chapter-packs',1,{upgrade(db){db.createObjectStore('packs');}});

function key(book:string,chapter:number){
  if(!/^[a-z0-9-]+$/.test(book)||!Number.isInteger(chapter)||chapter<1)throw new Error('Invalid chapter identifier.');
  return `${book}:${chapter}`;
}
async function checksum(pdf:Blob){const hash=await crypto.subtle.digest('SHA-256',await pdf.arrayBuffer());return Array.from(new Uint8Array(hash),value=>value.toString(16).padStart(2,'0')).join('');}
async function verified(pack:ChapterPack){
  return !!pack.pdf?.size&&/^[a-f0-9]{64}$/.test(pack.bundle?.sha256||'')&&Number.isInteger(pack.bundle?.pdf_page_offset)&&pack.bundle.pdf_page_offset>=0&&
    pack.bundle.chapters?.length===1&&pack.bundle.chapters[0].number===pack.bundle.chapter_number&&await checksum(pack.pdf)===pack.bundle.sha256;
}
export async function saveChapterPack(pack:ChapterPack){
  const id=key(pack.bundle.id,pack.bundle.chapter_number);
  if(!await verified(pack))throw new Error('Chapter download verification failed. Please retry.');
  const db=await database();try{await db.put('packs',{...pack,savedAt:Date.now()},id);}finally{db.close();}
  if(navigator.storage?.persist)await navigator.storage.persist().catch(()=>false);
}
export async function loadChapterPack(book:string,chapter:number):Promise<ChapterPack|undefined>{
  const id=key(book,chapter),db=await database();
  try{const pack:ChapterPack|undefined=await db.get('packs',id);if(!pack)return undefined;
    if(pack.bundle.id!==book||pack.bundle.chapter_number!==chapter||!await verified(pack)){await db.delete('packs',id);return undefined;}return pack;
  }finally{db.close();}
}
export async function listChapterPacks():Promise<ChapterPack[]>{
  const db=await database();try{const keys=await db.getAllKeys('packs'),valid:ChapterPack[]=[];
    for(const id of keys){const pack:ChapterPack=await db.get('packs',id);if(await verified(pack)&&id===key(pack.bundle.id,pack.bundle.chapter_number))valid.push(pack);else await db.delete('packs',id);}return valid;
  }finally{db.close();}
}
export async function removeChapterPack(book:string,chapter:number){const id=key(book,chapter),db=await database();try{await db.delete('packs',id);}finally{db.close();}}
