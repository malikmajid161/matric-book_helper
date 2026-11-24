import * as FS from 'expo-file-system/legacy';
import AsyncStorage from '@react-native-async-storage/async-storage';
import type {OfflineIndex} from './vectorMath';
import {installIndex,removeIndex} from './vectorDb';

export type Chapter = {number:number;title:string;start_page:number;end_page:number;topics:{id:string;title:string;page_number:number;key_points?:string[]}[];exercises:{id:string;text:string;page_number:number}[];pages:{page_number:number;text:string}[]};
export type Bundle = {id:string;title:string;edition:string;version:string;sha256:string;md5:string;chapters:Chapter[];offline_index?:OfflineIndex|null;chapter_number?:number;pdf_page_offset?:number;original_pdf_sha256?:string;source_book_version?:string;bytes?:number};
export type Download = {bundle:Bundle;pdfPath:string;bundlePath:string};
const root = `${FS.documentDirectory}books/`;
function validId(id:string) {if (!['physics','chemistry','mathematics','physics9','chemistry9'].includes(id)) throw new Error('Invalid book');}
async function checksum(path:string) {
  // Native streaming checksum avoids copying a 100 MB PDF into the JS heap.
  // Server verifies SHA-256; MD5 here detects transfer/storage corruption over HTTPS.
  const info = await FS.getInfoAsync(path,{md5:true});
  return info.exists ? info.md5 : undefined;
}
export async function load(id:string):Promise<Download|null> {
  validId(id);
  const raw = await AsyncStorage.getItem(`download:${id}`);
  if (!raw) return null;
  try {
    const value = JSON.parse(raw) as {pdfPath:string;bundlePath:string};
    const [pdf,bundleFile] = await Promise.all([FS.getInfoAsync(value.pdfPath),FS.getInfoAsync(value.bundlePath)]);
    if (!pdf.exists || !bundleFile.exists) throw new Error('Missing file');
    const bundle:Bundle = JSON.parse(await FS.readAsStringAsync(value.bundlePath));
    if (bundle.id !== id || !bundle.md5 || await checksum(value.pdfPath) !== bundle.md5) throw new Error('Invalid download');
    return {...value,bundle};
  } catch {await AsyncStorage.removeItem(`download:${id}`);return null;}
}
export async function save(id:string,base:string,code:string,onProgress:(value:number)=>void) {
  validId(id); await FS.makeDirectoryAsync(root,{intermediates:true});
  const headers = {'Authorization':`Bearer ${code}`};
  const response = await fetch(`${base}/books/${id}/bundle`,{headers});
  if (!response.ok) throw new Error('Textbook is not available. Retry later.');
  const bundle:Bundle = await response.json();
  const existing = await load(id);
  const reused = existing?.bundle.sha256 === bundle.sha256;
  // Unique filenames keep the previous verified copy valid if an update fails.
  const prefix = `${root}${id}-${Date.now()}`;
  const pdfPath = reused ? existing!.pdfPath : `${prefix}.pdf`, bundlePath = `${prefix}.json`;
  const oldRaw = await AsyncStorage.getItem(`download:${id}`);
  try {
    if (!reused) {
      const task = FS.createDownloadResumable(`${base}/books/${id}/download`,pdfPath,{headers}, event => onProgress(event.totalBytesExpectedToWrite > 0 ? event.totalBytesWritten/event.totalBytesExpectedToWrite : 0));
      const result = await task.downloadAsync();
      if (!result || result.status !== 200 || !bundle.md5 || await checksum(pdfPath) !== bundle.md5) throw new Error('Download integrity check failed. Please retry.');
    } else onProgress(1);
    await FS.writeAsStringAsync(bundlePath,JSON.stringify(bundle));
    await installIndex(bundle);
    await AsyncStorage.setItem(`download:${id}`,JSON.stringify({pdfPath,bundlePath}));
  } catch(error) {if(!reused)await FS.deleteAsync(pdfPath,{idempotent:true});await FS.deleteAsync(bundlePath,{idempotent:true});throw error;}
  if (oldRaw) {const old = JSON.parse(oldRaw); if(old.pdfPath!==pdfPath)await FS.deleteAsync(old.pdfPath,{idempotent:true});await FS.deleteAsync(old.bundlePath,{idempotent:true});}
  return load(id);
}
export async function remove(id:string) {
  const raw = await AsyncStorage.getItem(`download:${id}`); if (!raw) return;
  const value = JSON.parse(raw);
  await AsyncStorage.removeItem(`download:${id}`);
  await FS.deleteAsync(value.pdfPath,{idempotent:true});await FS.deleteAsync(value.bundlePath,{idempotent:true});
  await removeIndex(id);
}
