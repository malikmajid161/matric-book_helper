import React from 'react';
import {Text} from 'react-native';
export function SourceText({text,excerpt,color}:{text:string;excerpt:string;color:string}){
  const words=excerpt.trim().split(/\s+/).slice(0,18);
  const expression=words.length?new RegExp(words.map(word=>word.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('\\s+'),'i'):null;
  const match=expression?.exec(text);
  return <Text selectable style={{fontSize:14,lineHeight:23,color}}>{match?<>{text.slice(0,match.index)}<Text style={{backgroundColor:'#f7e49a',color:'#26331e'}}>{text.slice(match.index,match.index+match[0].length)}</Text>{text.slice(match.index+match[0].length)}</>:text}</Text>;
}
