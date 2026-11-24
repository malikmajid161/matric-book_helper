import type {Bundle} from './storage';
export function localSearch(bundle:Bundle, query:string, chapter?:number) {
  const stop=new Set('a an the is are what how why explain of in on to for and with'.split(' '));
  const words=[...new Set((query.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(word=>word.length>1&&!stop.has(word)))];
  if(!words.length)return [];
  return bundle.chapters.filter(row=>chapter===undefined||row.number===chapter).flatMap(row=>row.pages.map(page=>({...page,chapter_title:row.title,chapter_number:row.number,score:words.filter(word=>new Set(page.text.toLowerCase().match(/[a-z0-9]+/g)||[]).has(word)).length}))).filter(row=>row.score>=Math.min(2,words.length)).sort((a,b)=>b.score-a.score).slice(0,5);
}
