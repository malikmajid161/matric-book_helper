import React,{useState} from 'react';
import {Pressable,Text,View,useColorScheme} from 'react-native';
import type {Chapter} from './storage';
import {Explanation} from './Explanation';

type Question={id:string;text:string;page_number:number;solution?:string;solution_status?:string};
export function PracticeQuiz({chapters,onPage}:{chapters:Chapter[];onPage:(page:number)=>void}){
  const [questions,setQuestions]=useState<Question[]>([]),[revealed,setRevealed]=useState<Record<string,boolean>>({});
  const dark=useColorScheme()==='dark',ink=dark?'#e2eee6':'#20352b';
  function start(){const all=chapters.flatMap(row=>row.exercises) as Question[];for(let i=all.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[all[i],all[j]]=[all[j],all[i]];}setQuestions(all.slice(0,5));setRevealed({});}
  const button=(label:string,action:()=>void)=><Pressable accessibilityRole="button" onPress={action} style={{padding:13,borderRadius:8,backgroundColor:'#16734e',marginVertical:8}}><Text style={{color:'white',textAlign:'center'}}>{label}</Text></Pressable>;
  return <View style={{padding:18,borderRadius:12,borderWidth:1,borderColor:dark?'#345140':'#d6e6db',marginVertical:12}}><Text style={{color:ink,fontSize:19,fontWeight:'700'}}>Offline practice quiz</Text><Text style={{color:ink,lineHeight:22,marginVertical:10}}>Five random questions from your saved textbook exercises. Checked solutions can be revealed; other questions link to the source page.</Text>{button('Start / shuffle practice quiz',start)}{questions.map((row,i)=><View key={row.id} style={{marginVertical:12}}><Text selectable style={{color:ink,fontSize:15,lineHeight:24}}>{i+1}. {row.text}</Text>{row.solution_status==='checked'&&row.solution?button(revealed[row.id]?'Hide checked solution':'Show checked solution',()=>setRevealed(previous=>({...previous,[row.id]:!previous[row.id]}))):<Text style={{color:ink,marginVertical:8}}>Worked solution awaiting checking.</Text>}{revealed[row.id]&&row.solution&&<Explanation answer={row.solution}/>} {button(`Open textbook page ${row.page_number}`,()=>onPage(row.page_number))}</View>)}{!chapters.some(row=>row.exercises.length)&&<Text style={{color:ink}}>No reviewed questions saved for this selection yet.</Text>}</View>;
}
