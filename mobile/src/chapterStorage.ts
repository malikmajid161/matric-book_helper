import * as FS from 'expo-file-system/legacy';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {Bundle,Download} from './storage';
import {removeIndexVersion} from './vectorDb';

const root=`${FS.documentDirectory}chapters/`;
const key=(book:string,chapter:number)=>{if(!['physics','chemistry','mathematics','physics9','chemistry9'].includes(book)||!Number.isInteger(chapter)||chapter<1)throw Error('Invalid chapter');return `chapter:${book}:${chapter}`;};
export async function loadChapter(book:string,chapter:number):Promise<Download|null>{
  const raw=await AsyncStorage.getItem(key(book,chapter));if(!raw)return null;
  try{const paths=JSON.parse(raw);const pdf=await FS.getInfoAsync(paths.pdfPath,{md5:true});const meta=await FS.getInfoAsync(paths.bundlePath);if(!pdf.exists||!meta.exists)throw Error('Missing file');const bundle:Bundle=JSON.parse(await FS.readAsStringAsync(paths.bundlePath));if(bundle.id!==book||bundle.chapter_number!==chapter||pdf.md5!==bundle.md5)throw Error('Corrupt file');return {...paths,bundle};}catch{await AsyncStorage.removeItem(key(book,chapter));return null;}
}
export async function listChapters(book:string){const keys=await AsyncStorage.getAllKeys();const packs=await Promise.all(keys.filter(value=>value.startsWith(`chapter:${book}:`)).map(value=>loadChapter(book,Number(value.split(':')[2]))));return packs.filter((value):value is Download=>!!value);}
export async function saveChapter(book:string,chapter:number,base:string,token:string,onProgress:(n:number)=>void){
  const storageKey=key(book,chapter);const existing=await loadChapter(book,chapter);if(existing)return existing;
  const headers={Authorization:`Bearer ${token}`};const response=await fetch(`${base}/books/${book}/chapters/${chapter}/bundle`,{headers});if(!response.ok)throw Error('Chapter unavailable. Retry later.');const bundle:Bundle=await response.json();
  await FS.makeDirectoryAsync(root,{intermediates:true});const prefix=`${root}${book}-${chapter}-${Date.now()}`;const paths={pdfPath:`${prefix}.pdf`,bundlePath:`${prefix}.json`};
  try{const task=FS.createDownloadResumable(`${base}/books/${book}/chapters/${chapter}/download`,paths.pdfPath,{headers},event=>onProgress(event.totalBytesExpectedToWrite>0?event.totalBytesWritten/event.totalBytesExpectedToWrite:0));const result=await task.downloadAsync();const info=await FS.getInfoAsync(paths.pdfPath,{md5:true});if(result?.status!==200||!info.exists||!bundle.md5||info.md5!==bundle.md5)throw Error('Chapter verification failed. Retry.');await FS.writeAsStringAsync(paths.bundlePath,JSON.stringify(bundle));await AsyncStorage.setItem(storageKey,JSON.stringify(paths));return {...paths,bundle};}catch(error){await FS.deleteAsync(paths.pdfPath,{idempotent:true});await FS.deleteAsync(paths.bundlePath,{idempotent:true});throw error;}
}
export async function removeChapter(book:string,chapter:number){const raw=await AsyncStorage.getItem(key(book,chapter));if(!raw)return;const saved=await loadChapter(book,chapter);const paths=JSON.parse(raw);if(saved)await removeIndexVersion(book,saved.bundle.version);await FS.deleteAsync(paths.pdfPath,{idempotent:true});await FS.deleteAsync(paths.bundlePath,{idempotent:true});await AsyncStorage.removeItem(key(book,chapter));}
