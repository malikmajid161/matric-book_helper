import type {Bundle} from './storage';

type SavedQuestion={id:string;text:string;page_number:number;solution_status?:string;solution?:string;solution_source_pages?:number[]};

// Only harmless prose punctuation is ignored. Digits, decimal points within a
// number, brackets, powers, signs, fractions and other mathematical symbols stay.
function normalizedQuestion(text:string){
  return text.toLowerCase().trim()
    .replace(/^(?:q(?:uestion)?\s*)?\d+(?:\.\d+)+(?:[.)])?\s+/i,'')
    .replace(/^(?:q(?:uestion)?\s*)?\d+[.)]\s+/i,'')
    .replace(/[?"“”]/g,' ')
    .replace(/\.(?!\d)/g,' ')
    .replace(/\s*([+−\-×÷=<>/^()\[\]{}])\s*/g,'$1')
    .replace(/\s+/g,' ').trim();
}

export function resolveSavedQuestion(query:string,bundle:Bundle,chapter?:number){
  const normalized=normalizedQuestion(query);if(!normalized)return null;
  const matches=bundle.chapters.filter(owner=>chapter===undefined||owner.number===chapter)
    .flatMap(owner=>(owner.exercises as SavedQuestion[]).filter(item=>item.solution_status==='checked'&&item.solution?.trim()
      &&item.page_number>=owner.start_page&&item.page_number<=(owner.end_page??item.page_number)
      &&normalizedQuestion(item.text)===normalized).map(item=>({owner,item})));
  if(!matches.length)return null;
  const answers=new Set(matches.map(({item})=>item.solution!.trim().replace(/\s+/g,' ')));
  if(answers.size!==1)return null;
  const {owner,item}=matches[0];
  const questionPage=owner.pages.find(page=>page.page_number===item.page_number);
  const evidencePages=[...new Set(item.solution_source_pages?.length?item.solution_source_pages:[item.page_number])];
  // Declared evidence must be present in this chapter's saved original pages.
  // Never fabricate a source excerpt from the generated solution itself.
  const evidence=evidencePages.map(number=>owner.pages.find(page=>page.page_number===number));
  if(evidence.some(page=>!page?.text.trim()))return null;
  const pages=[...(questionPage?.text.trim()?[questionPage]:[]),...evidence.filter(page=>page!.page_number!==questionPage?.page_number)];
  if(!pages.length)return null;
  const sources=pages.map((page,index)=>({id:`${bundle.id}:${page!.page_number}:saved-solution`,citation:index+1,
    book:bundle.id,chapter_number:owner.number,chapter_title:owner.title,page_number:page!.page_number,text:page!.text,distance:0}));
  const citationFor=(number:number)=>sources.find(source=>source.page_number===number)?.citation;
  const questionCitation=citationFor(item.page_number);
  const evidenceCitations=evidencePages.map(citationFor).filter((value):value is number=>value!==undefined).map(value=>`[${value}]`).join(' ');
  // Stored citation numbering may belong to a different retrieval response.
  // Rebind it to the original saved pages above instead of reusing stale IDs.
  const solution=item.solution!.replace(/\[\d+\]/g,'').trim();
  return {answer:`## Question\n${item.text}${questionCitation?` [${questionCitation}]`:''}\n\n## Saved worked solution\n${solution}\n\n## Textbook basis\nThis checked study solution is independently derived from the saved textbook material. It is not an official board answer key. ${evidenceCitations}`,supported:true,sources};
}
