import type {Bundle} from './types';

type SavedExercise={id:string;text:string;page_number:number;exercise?:string;question_number?:number;part?:string;solution_status?:string;solution?:string};
const exercisePattern=/\b(?:exercise|excersise|excercise|excercize|exersise|exersize|exercice|exer|ex)\.?\s*(\d+)\s*[.\-]\s*(\d+)\b/gi;
export function resolveSavedExercise(query:string,bundle:Bundle,chapter?:number){
  const matches=[...query.matchAll(new RegExp(exercisePattern))];if(!matches.length)return null;
  const refs=new Set(matches.map(match=>`${Number(match[1])}.${Number(match[2])}`));
  if(refs.size>1)return {answer:'## Choose one exercise\nPlease ask for one exercise at a time, for example: ex 1.1 q 2.',supported:false,sources:[]};
  const exercise=[...refs][0], question=query.match(/\b(?:questions?|ques|qn|q)\.?\s*#?\s*(\d+)\b/i);
  const owned=bundle.chapters.filter(row=>chapter===undefined||row.number===chapter).flatMap(owner=>(owner.exercises as SavedExercise[]).filter(item=>item.exercise===exercise&&(!question||item.question_number===Number(question[1]))&&item.page_number>=owner.start_page&&item.page_number<=(owner.end_page??item.page_number)).map(item=>({owner,item})));
  if(!owned.length)return {answer:`## Exercise ${exercise}\nI understood the exercise reference, but its exact questions have not been reviewed in this saved book yet.\n\n## Next step\nOpen the original PDF or paste one complete question, including powers and signs. I will not invent the missing questions.`,supported:false,sources:[]};
  const questionsOnly=/\b(?:all\s+q|questions|list|show.*q|give.*q|sawal|sawalat)/i.test(query)&&!/sol|solve|answer|\bhal\b|\bjawab\b/i.test(query);
  const introduction=questionsOnly?'Questions checked against the original textbook page.':'Saved worked solutions are independently derived study help, not an official board answer key.';
  const parts=[`## Exercise ${exercise}`,introduction];
  const sources:{id:string;citation:number;book:string;chapter_number:number;chapter_title:string;page_number:number;text:string;distance:number}[]=[];
  const pageIds=new Map<string,number>();let complete=true;
  for(const {owner,item} of owned){
    const sourceKey=`${owner.number}:${item.page_number}`;
    if(!pageIds.has(sourceKey)){
      pageIds.set(sourceKey,sources.length+1);
      sources.push({id:`${bundle.id}:${item.page_number}:exercise`,citation:pageIds.get(sourceKey)!,book:bundle.id,chapter_number:owner.number,chapter_title:owner.title,page_number:item.page_number,text:owned.filter(row=>row.owner.number===owner.number&&row.item.page_number===item.page_number).map(row=>row.item.text).join('\n'),distance:0});
    }
    const citation=pageIds.get(sourceKey)!;
    parts.push(`## Question ${item.question_number}${item.part?` (${item.part})`:''}`,`${item.text} [${citation}]`);
    if(!questionsOnly){
      const solution=item.solution;
      if(item.solution_status==='checked'&&solution)parts.push(`${solution} [${citation}]`);
      else{complete=false;parts.push('This solution is still awaiting checking. Ask one complete question for online help.');}
    }
  }
  return {answer:parts.join('\n\n'),supported:questionsOnly||complete,sources};
}
