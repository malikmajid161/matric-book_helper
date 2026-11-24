import React,{useEffect,useMemo,useRef,useState} from 'react';
import {ActivityIndicator,Modal,Pressable,StyleSheet,Text,TextInput,View,useColorScheme} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import Pdf,{PdfRef} from 'react-native-pdf';

type Props={uri:string;page:number;onClose:()=>void};

/** Open the already verified local PDF. Never fetch a remote document here. */
export function TextbookReader({uri,page,onClose}:Props){
  const requested=Math.max(1,Number.isFinite(page)?Math.floor(page):1);
  const [current,setCurrent]=useState(requested),[total,setTotal]=useState(0),[input,setInput]=useState(String(requested));
  const [loading,setLoading]=useState(true),[error,setError]=useState(''),[attempt,setAttempt]=useState(0);
  const ref=useRef<PdfRef>(null);
  const dark=useColorScheme()==='dark';
  const colors={background:dark?'#102119':'#f4f8f5',surface:dark?'#1b3025':'#ffffff',ink:dark?'#edf6ef':'#18362a',line:dark?'#345140':'#d6e6db',muted:dark?'#b7c9bd':'#557463'};
  const local=uri.startsWith('file://')||uri.startsWith('content://');
  const source=useMemo(()=>({uri,cache:false}),[uri]);
  useEffect(()=>{setCurrent(requested);setInput(String(requested));setTotal(0);setLoading(true);setError('');},[uri,requested]);
  function jump(value:number){
    if(!Number.isFinite(value)||total===0)return;
    const next=Math.min(total,Math.max(1,Math.floor(value)));
    ref.current?.setPage(next);setCurrent(next);setInput(String(next));
  }
  function retry(){setError('');setLoading(true);setTotal(0);setAttempt(value=>value+1);}
  const button=(label:string,onPress:()=>void,disabled=false)=><Pressable accessibilityRole="button" accessibilityLabel={label} disabled={disabled} onPress={onPress} style={[styles.button,{opacity:disabled?.45:1}]}><Text style={styles.buttonText}>{label}</Text></Pressable>;
  return <Modal visible animationType="slide" onRequestClose={onClose} presentationStyle="fullScreen"><SafeAreaView style={[styles.safe,{backgroundColor:colors.background}]}>
    <View style={[styles.header,{backgroundColor:colors.surface,borderColor:colors.line}]}><View style={styles.heading}><Text style={[styles.title,{color:colors.ink}]}>Your textbook</Text><Text style={[styles.caption,{color:colors.muted}]}>Saved on this device · available offline</Text></View>{button('Close',onClose)}</View>
    <View style={[styles.navigation,{backgroundColor:colors.surface,borderColor:colors.line}]}>
      {button('Previous',()=>jump(current-1),loading||current<=1||!!error)}
      <View style={styles.pageField}><Text style={[styles.caption,{color:colors.muted}]}>PDF page</Text><View style={styles.pageRow}><TextInput accessibilityLabel="PDF page number" keyboardType="number-pad" returnKeyType="go" selectTextOnFocus maxLength={5} value={input} onChangeText={value=>setInput(value.replace(/\D/g,''))} onSubmitEditing={()=>jump(Number(input))} style={[styles.pageInput,{color:colors.ink,borderColor:colors.line}]} editable={!loading&&!error}/><Text style={[styles.caption,{color:colors.muted}]}>/ {total||'…'}</Text></View></View>
      {button('Go',()=>jump(Number(input)),loading||!input||!!error)}
      {button('Next',()=>jump(current+1),loading||current>=total||!!error)}
    </View>
    {!local||error?<View style={styles.state}><Text style={[styles.stateTitle,{color:colors.ink}]}>Could not open the saved PDF</Text><Text style={[styles.stateText,{color:colors.muted}]}>{!local?'This reader opens downloaded books only. Download the textbook first.':'Try opening it again. If its files were removed, return to the library and download the book again.'}</Text>{local&&button('Retry',retry)}{button('Back to study',onClose)}</View>:<View style={styles.document}>
      <Pdf key={`${uri}:${attempt}`} ref={ref} source={source} page={requested} fitPolicy={0} minScale={1} maxScale={5} enableDoubleTapZoom enableAnnotationRendering trustAllCerts={false} style={styles.pdf}
        onLoadComplete={numberOfPages=>{setTotal(numberOfPages);setLoading(false);const next=Math.min(numberOfPages,requested);setCurrent(next);setInput(String(next));if(next!==requested)ref.current?.setPage(next);}}
        onPageChanged={(number,numberOfPages)=>{setCurrent(number);setInput(String(number));setTotal(numberOfPages);}}
        onError={()=>{setLoading(false);setError('Saved PDF could not be rendered.');}}
        renderActivityIndicator={()=><ActivityIndicator size="large" color="#248358"/>}/>
      {loading&&<View pointerEvents="none" style={[styles.loading,{backgroundColor:colors.background}]}><ActivityIndicator size="large" color="#248358"/><Text style={[styles.stateText,{color:colors.muted}]}>Opening your saved book…</Text></View>}
    </View>}
    <Text style={[styles.footer,{color:colors.muted}]}>Pinch to zoom. Page numbers refer to the PDF, which may differ from printed page numbers.</Text>
  </SafeAreaView></Modal>;
}

const styles=StyleSheet.create({safe:{flex:1},header:{paddingHorizontal:16,paddingVertical:12,flexDirection:'row',alignItems:'center',gap:10,borderBottomWidth:1},heading:{flex:1},title:{fontSize:19,fontWeight:'700'},caption:{fontSize:11,lineHeight:17},navigation:{paddingHorizontal:10,paddingVertical:10,borderBottomWidth:1,flexDirection:'row',alignItems:'center',justifyContent:'space-between',gap:6},button:{backgroundColor:'#176d48',paddingHorizontal:12,paddingVertical:11,borderRadius:8,alignItems:'center'},buttonText:{color:'#fff',fontSize:12,fontWeight:'600'},pageField:{alignItems:'center',gap:2},pageRow:{flexDirection:'row',alignItems:'center',gap:5},pageInput:{minWidth:42,paddingHorizontal:6,paddingVertical:5,borderWidth:1,borderRadius:5,textAlign:'center',fontSize:14},document:{flex:1},pdf:{flex:1,width:'100%',backgroundColor:'#dce5df'},loading:{position:'absolute',top:0,right:0,bottom:0,left:0,justifyContent:'center',alignItems:'center',gap:12},state:{flex:1,justifyContent:'center',alignItems:'center',padding:28,gap:16},stateTitle:{fontSize:20,fontWeight:'700',textAlign:'center'},stateText:{fontSize:14,lineHeight:23,textAlign:'center'},footer:{fontSize:10,lineHeight:16,textAlign:'center',padding:10}});
