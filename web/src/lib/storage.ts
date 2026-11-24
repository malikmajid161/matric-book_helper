import {openDB} from 'idb';
import type {Answer, Bundle, CachedBook} from './types';
const database = () => openDB('ptb-scholar', 2, {upgrade(db) {if(!db.objectStoreNames.contains('books'))db.createObjectStore('books');if(!db.objectStoreNames.contains('answers'))db.createObjectStore('answers');}});
export async function checksum(blob: Blob) {
  const hash = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
  return Array.from(new Uint8Array(hash), byte => byte.toString(16).padStart(2, '0')).join('');
}
export async function saveBook(bundle: Bundle, pdf: Blob) {
  if (pdf.size === 0 || await checksum(pdf) !== bundle.sha256) throw new Error('Download verification failed. Please download again.');
  const db = await database();
  try {await db.put('books', {bundle, pdf, savedAt: Date.now()} satisfies CachedBook, bundle.id);} finally {db.close();}
  if (navigator.storage?.persist) await navigator.storage.persist().catch(() => false);
}
export async function loadBook(id: string): Promise<CachedBook | undefined> {
  const db = await database();
  try {
    const value: CachedBook | undefined = await db.get('books', id);
    if (!value) return undefined;
    if (!value.pdf?.size || !value.bundle?.chapters || await checksum(value.pdf) !== value.bundle.sha256) {await db.delete('books', id); return undefined;}
    return value;
  } finally {db.close();}
}
export async function removeBook(id: string) {
  const db = await database();
  try {await db.delete('books', id);} finally {db.close();}
}
export async function allBooks(): Promise<CachedBook[]> {
  const db = await database();
  try {return await db.getAll('books');} finally {db.close();}
}
const answerKey=(profile:string, bundle:Bundle, question:string)=>`${profile}:${bundle.id}:${bundle.version}:${question.trim().toLowerCase()}`;
export async function saveAnswer(profile:string,bundle:Bundle,question:string,result:Answer){
  if(!result.supported)return;
  const db=await database();
  try{await db.put('answers',{result,savedAt:Date.now()},answerKey(profile,bundle,question));const keys=await db.getAllKeys('answers');if(keys.length>150){const entries=await Promise.all(keys.map(async key=>({key,date:(await db.get('answers',key)).savedAt})));entries.sort((a,b)=>a.date-b.date);for(const row of entries.slice(0,keys.length-150))await db.delete('answers',row.key);}}finally{db.close();}
}
export async function loadAnswer(profile:string,bundle:Bundle,question:string):Promise<Answer|undefined>{
  const db=await database();try{return (await db.get('answers',answerKey(profile,bundle,question)))?.result;}finally{db.close();}
}
