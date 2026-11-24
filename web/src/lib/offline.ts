import type {Bundle, Source} from './types';
const stop = new Set('a an the is are was were what why how explain give me of in on to for and or with from does do can please'.split(' '));
function terms(value: string) {return (value.toLowerCase().match(/[a-z0-9]+/g) || []).filter(word => word.length > 1 && !stop.has(word));}
/** Local ranked passage search. Returns verbatim page text, never generated answers. */
export function findPassages(bundle: Bundle, query: string, chapter?: number): Source[] {
  const words = [...new Set(terms(query))];
  if (!words.length) return [];
  const documents = bundle.chapters.filter(row => chapter === undefined || row.number === chapter).flatMap(row => (row.pages || []).flatMap(page => {
    const paragraphs = page.text.split(/\n\s*\n/).filter(text => text.trim().length > 30);
    return (paragraphs.length ? paragraphs : [page.text]).flatMap(text => {
      const tokens = text.split(/\s+/);
      const parts = [];
      for (let offset = 0; offset < tokens.length; offset += 160) parts.push(tokens.slice(offset, offset + 200).join(' '));
      return parts.map((part, index) => ({id: `${bundle.id}:${page.page_number}:${index}`, book: bundle.id, chapter_number: row.number, chapter_title: row.title, page_number: page.page_number, text: part, tokens: terms(part)}));
    });
  }));
  const counts = words.map(word => documents.filter(doc => doc.tokens.includes(word)).length);
  return documents.map(doc => {
    const matches = words.filter(word => doc.tokens.includes(word)).length;
    const score = words.reduce((sum, word, index) => {
      const frequency = doc.tokens.filter(token => token === word).length;
      return sum + Math.log(1 + (documents.length + 1) / (counts[index] + 1)) * frequency / (frequency + 1.2 + doc.tokens.length / 200);
    }, 0);
    return {...doc, score, matches};
  }).filter(doc => doc.matches >= Math.min(2, words.length)).sort((a,b) => b.score - a.score).slice(0,5).map((doc, index) => ({id:doc.id,book:doc.book,chapter_number:doc.chapter_number,chapter_title:doc.chapter_title,page_number:doc.page_number,text:doc.text,citation:index+1,distance:0}));
}
