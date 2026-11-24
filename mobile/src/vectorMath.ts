export type VectorDocument={id:string;chapter_number:number;chapter_title:string;page_number:number;text:string;vector:number[]};
export type OfflineIndex={model:string;dimensions:number;vocabulary:string[];idf:number[];projection:number[][];documents:VectorDocument[]};
const stop=new Set('a an the is are was were what why how explain give me of in on to for and or with from does do can please this that which have has it as be by its'.split(' '));
export function queryVector(index:Omit<OfflineIndex,'documents'>,query:string){
  const counts=new Map<string,number>();
  for(const word of query.toLowerCase().match(/[a-z0-9]+/g)||[])if(word.length>1&&!stop.has(word))counts.set(word,(counts.get(word)||0)+1);
  const vector=Array(index.dimensions).fill(0) as number[];
  index.vocabulary.forEach((word,i)=>{const count=counts.get(word);if(count){const weight=(1+Math.log(count))*index.idf[i];for(let d=0;d<vector.length;d++)vector[d]+=weight*index.projection[i][d];}});
  const norm=Math.hypot(...vector);return norm>1e-10?vector.map(value=>value/norm):null;
}
export function rankVectors(documents:VectorDocument[],query:number[],chapter?:number){
  return documents.filter(row=>chapter===undefined||row.chapter_number===chapter)
    .map(row=>({...row,score:row.vector.reduce((sum,value,i)=>sum+value*query[i],0)}))
    .filter(row=>row.score>=0.25).sort((a,b)=>b.score-a.score).slice(0,5)
    .map(({vector:_,...row},i)=>({...row,citation:i+1}));
}
