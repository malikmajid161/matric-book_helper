const markers=new Set('kya kaise samjhao samjha samjhaein hai hain mein mujhe batao sawal sawalat jawab hal karo karein chahiye ki ke ka se'.split(' '));
const strong=new Set(['samjhao','samjhaein','batao']);
const aliases:Record<string,string>={garmi:'heat',hararat:'temperature',awaz:'sound',awaaz:'sound',roshni:'light',bijli:'electricity',zarraat:'particles',tezab:'acid',namak:'salt'};
const retrievalStop=new Set([...markers,...'mujhay mujhy iska iski iske yeh ye woh wo kyun kyu samjhayen samjhaen samjha do dein bata bataein bataen bare baray baare baat kya kese kesay mujko hum ko aur bhi asaan aasan alfaaz lafzon zara please'.split(' ')]);
export function detectLanguage(query:string):'english'|'roman-urdu'{
  const text=query.toLowerCase();
  if(/\b(?:in\s+english|english\s+(?:mein|me)|(?:answer|explain|reply)\s+(?:in\s+)?english)\b/.test(text))return 'english';
  if(/\broman\s+urdu\b/.test(text))return 'roman-urdu';
  const words=new Set(text.match(/[a-z]+/g)||[]);
  return [...words].some(word=>strong.has(word))||[...words].filter(word=>markers.has(word)).length>=2?'roman-urdu':'english';
}
export function retrievalText(query:string){
  const words=query.toLowerCase().match(/[a-z0-9]+/g)||[];
  const normalized=words.filter(word=>!retrievalStop.has(word)).map(word=>aliases[word]||word);
  return normalized.length?normalized.join(' '):query;
}
