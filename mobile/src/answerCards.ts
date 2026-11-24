export function answerCards(answer:string){
  const cards:{title:string;body:string}[]=[];let title='Explanation',lines:string[]=[];
  const flush=()=>{if(lines.join('\n').trim())cards.push({title,body:lines.join('\n').trim()});lines=[];};
  for(const line of answer.split('\n')){const heading=line.match(/^#{1,3}\s+(.+)$/);if(heading){flush();title=heading[1];}else lines.push(line);}
  flush();return cards;
}
