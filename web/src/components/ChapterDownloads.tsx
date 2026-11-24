'use client';
import {useEffect,useState} from 'react';
import type {Book} from '@/lib/types';
import {type ChapterBundle,type ChapterPack,listChapterPacks,loadChapterPack,removeChapterPack,saveChapterPack} from '@/lib/chapterStorage';

const BASE=(process.env.NEXT_PUBLIC_API_URL||'http://localhost:8000').replace(/\/$/,'');
const packKey=(book:string,chapter:number)=>`${book}:${chapter}`;
const bytes=(size:number)=>size>=1024*1024?`${(size/1024/1024).toFixed(1)} MB`:`${Math.max(1,Math.round(size/1024))} KB`;
const headers=()=>({'Authorization':`Bearer ${sessionStorage.getItem('studyToken')||''}`,'X-Study-Code':sessionStorage.getItem('studyCode')||''});

async function download(bundle:ChapterBundle,report:(received:number,total:number)=>void){
  const response=await fetch(`${BASE}/books/${encodeURIComponent(bundle.id)}/chapters/${bundle.chapter_number}/download`,{headers:headers(),signal:AbortSignal.timeout(180000)});
  if(!response.ok)throw new Error(`Chapter download failed (${response.status}). Please retry.`);
  const total=Number(response.headers.get('Content-Length'))||bundle.bytes||0;
  if(!response.body){const pdf=await response.blob();report(pdf.size,total);return pdf;}
  const reader=response.body.getReader(),chunks:Uint8Array<ArrayBuffer>[]= [];let received=0;
  for(;;){const {done,value}=await reader.read();if(done)break;chunks.push(new Uint8Array(value));received+=value.byteLength;report(received,total);}
  return new Blob(chunks,{type:'application/pdf'});
}

export function ChapterDownloads({books,onStudy}:{books:Book[];onStudy:(pack:ChapterPack)=>void}){
  const [packs,setPacks]=useState<Record<string,ChapterPack>>({}),[busy,setBusy]=useState(''),[error,setError]=useState(''),[retry,setRetry]=useState<{book:Book;chapter:number}|null>(null),[progress,setProgress]=useState({received:0,total:0});
  useEffect(()=>{let active=true;listChapterPacks().then(rows=>{if(active)setPacks(Object.fromEntries(rows.map(row=>[packKey(row.bundle.id,row.bundle.chapter_number),row])));}).catch(()=>{if(active)setError('Browser storage is unavailable. Allow storage and retry.');});return()=>{active=false;};},[]);
  async function study(book:Book,chapter:number){
    if(busy)return;const id=packKey(book.id,chapter);setBusy(id);setError('');setRetry(null);setProgress({received:0,total:0});
    try{
      // Check verified device storage before any network call. Valid PDFs download once.
      const saved=await loadChapterPack(book.id,chapter);
      if(saved){setPacks(previous=>({...previous,[id]:saved}));onStudy(saved);return;}
      const response=await fetch(`${BASE}/books/${encodeURIComponent(book.id)}/chapters/${chapter}/bundle`,{headers:headers(),signal:AbortSignal.timeout(90000)});
      if(!response.ok){const detail=await response.json().catch(()=>({}));throw new Error(detail.detail||'This chapter is not ready to download. Please retry.');}
      const bundle=await response.json() as ChapterBundle;
      if(bundle.id!==book.id||bundle.chapter_number!==chapter)throw new Error('Server returned a different chapter. Download stopped.');
      const pdf=await download(bundle,(received,total)=>setProgress({received,total}));
      const pack={bundle,pdf};await saveChapterPack(pack);setPacks(previous=>({...previous,[id]:pack}));onStudy(pack);
    }catch(cause){setError(cause instanceof Error?cause.message:'Could not download this chapter. Please retry.');setRetry({book,chapter});}
    finally{setBusy('');}
  }
  async function remove(pack:ChapterPack){
    if(busy||!window.confirm(`Remove the saved chapter “${pack.bundle.chapters[0]?.title}”? You can download it again. Practice progress will be kept.`))return;
    const id=packKey(pack.bundle.id,pack.bundle.chapter_number);setBusy(id);setError('');
    try{await removeChapterPack(pack.bundle.id,pack.bundle.chapter_number);setPacks(previous=>{const next={...previous};delete next[id];return next;});}
    catch{setError('The chapter could not be removed. Please retry.');}finally{setBusy('');}
  }
  return <section className="panel" aria-label="Download individual chapters" style={{marginTop:24}}>
    <h2>Download just the chapter you need</h2><p className="muted">Save a smaller PDF and its study data once. Open saved chapters without internet.</p>
    {!!error&&<div role="alert" className="error-banner"><span>{error}</span>{retry&&<button className="text-btn" disabled={!!busy} onClick={()=>void study(retry.book,retry.chapter)}>Retry chapter download</button>}</div>}
    {books.map(book=><details key={book.id} style={{padding:'14px 0',borderTop:'1px solid var(--line)'}}><summary style={{fontWeight:600}}>{book.title} · Class {/9(?:$|-)/.test(book.id)?'9':'10'} · {book.chapters.length} chapters</summary>
      {!book.chapters.length&&<p className="muted" style={{marginTop:12}}>Chapter pages are still being prepared. The original book is available from the textbook shelf.</p>}
      {book.chapters.map(chapter=>{const id=packKey(book.id,chapter.number),saved=packs[id],working=busy===id;return <div key={id} style={{padding:'16px 0',borderBottom:'1px solid var(--line)'}}>
        <h3 style={{marginBottom:6}}>{chapter.number}. {chapter.title}</h3><p className="muted">Original PDF pages {chapter.start_page}–{chapter.end_page||chapter.start_page}{saved?` · ${bytes(saved.pdf.size)} saved on device`:' · Downloads this chapter only'}</p>
        {working&&<div role="status" aria-live="polite"><p>{progress.received?`${bytes(progress.received)}${progress.total?` / ${bytes(progress.total)}`:''} · Downloading and verifying…`:'Preparing chapter…'}</p>{progress.total>0&&<progress aria-label={`Downloading ${chapter.title}`} value={progress.received} max={progress.total} style={{width:'100%'}}/>}</div>}
        <div className="answer-actions"><button disabled={!!busy} onClick={()=>void study(book,chapter.number)} aria-label={`${saved?'Open saved':'Download'} ${book.title} chapter ${chapter.number}`}>{saved?'Open saved chapter →':'↓ Download chapter'}</button>{saved&&<button disabled={!!busy} onClick={()=>void remove(saved)} aria-label={`Remove ${book.title} chapter ${chapter.number} download`}>Remove download</button>}</div>
      </div>;})}
    </details>)}
  </section>;
}
