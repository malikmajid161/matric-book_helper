import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

export function StudyAnswer({answer}:{answer:string}){
  const cards:{title:string;body:string}[]=[];let title='Explanation',lines:string[]=[];
  const flush=()=>{if(lines.join('\n').trim())cards.push({title,body:lines.join('\n').trim()});lines=[];};
  for(const line of answer.split('\n')){const heading=line.match(/^#{1,3}\s+(.+)$/);if(heading){flush();title=heading[1];}else lines.push(line);}flush();
  return <div className="study-answer">{cards.map((card,i)=><section className="study-answer-card" key={i}><h3>{card.title}</h3><div className="markdown"><ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>{card.body}</ReactMarkdown></div></section>)}</div>;
}
