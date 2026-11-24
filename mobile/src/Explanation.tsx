import React from 'react';
import {StyleSheet,Text,View,useColorScheme} from 'react-native';
import {answerCards} from './answerCards';
export function Explanation({answer}:{answer:string}){
  const dark=useColorScheme()==='dark';return <View style={styles.cards}>{answerCards(answer).map((card,i)=><View key={i} style={[styles.card,{backgroundColor:dark?'#203b2d':'#f0f8f2',borderColor:dark?'#365843':'#dcecdf'}]}><Text style={[styles.title,{color:dark?'#8ed0a6':'#17623e'}]}>{card.title}</Text><Text selectable style={[styles.body,{color:dark?'#e2eee6':'#20352b'}]}>{card.body.replace(/\*\*(.*?)\*\*/g,'$1').replace(/^[-*] /gm,'• ')}</Text></View>)}</View>;
}
const styles=StyleSheet.create({cards:{gap:12,marginVertical:12},card:{borderWidth:1,borderRadius:12,padding:16},title:{fontSize:16,fontWeight:'700',marginBottom:10},body:{fontSize:15,lineHeight:25}});
