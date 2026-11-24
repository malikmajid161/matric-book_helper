/** Highlight the retrieved passage inside its original stored page, never generated prose. */
export function SourceText({text,excerpt}:{text:string;excerpt:string}){
  const words=excerpt.trim().split(/\s+/).slice(0,220);
  const expression=words.length?new RegExp(words.map(word=>word.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('\\s+'),'i'):null;
  const match=expression?.exec(text);
  if(!match)return <p style={{whiteSpace:'pre-wrap'}}>{text}</p>;
  return <p style={{whiteSpace:'pre-wrap'}}>{text.slice(0,match.index)}<mark style={{background:'#f7e49a',color:'#26331e',padding:'2px 0'}}>{text.slice(match.index,match.index+match[0].length)}</mark>{text.slice(match.index+match[0].length)}</p>;
}
