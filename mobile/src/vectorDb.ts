import * as SQLite from 'expo-sqlite';
import type {Bundle} from './storage';
import {OfflineIndex,VectorDocument,queryVector,rankVectors} from './vectorMath';

let opening:Promise<SQLite.SQLiteDatabase>|undefined;
async function database(){
  if(!opening)opening=(async()=>{const db=await SQLite.openDatabaseAsync('ptb-vectors.db');await db.execAsync(`
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS models(book TEXT NOT NULL, version TEXT NOT NULL, model TEXT NOT NULL, metadata TEXT NOT NULL, PRIMARY KEY(book,version));
    CREATE TABLE IF NOT EXISTS vectors(book TEXT NOT NULL, version TEXT NOT NULL, id TEXT NOT NULL, chapter INTEGER NOT NULL, document TEXT NOT NULL, PRIMARY KEY(book,version,id));
    CREATE INDEX IF NOT EXISTS vector_scope ON vectors(book,version,chapter);
  `);return db;})().catch(error=>{opening=undefined;throw error;});
  return opening;
}
export async function installIndex(bundle:Bundle){
  const index=bundle.offline_index;if(!index)return;
  if(index.model!=='lsa-tfidf-1'||index.dimensions<1||index.dimensions>64||index.documents.some(row=>row.vector.length!==index.dimensions))throw new Error('Unsupported offline index. Update the app.');
  const db=await database();const stored=await db.getFirstAsync<{model:string}>('SELECT model FROM models WHERE book=? AND version=?',bundle.id,bundle.version);
  if(stored?.model===index.model)return;
  const {documents,...metadata}=index;
  await db.withExclusiveTransactionAsync(async tx=>{
    await tx.runAsync('DELETE FROM vectors WHERE book=? AND version=?',bundle.id,bundle.version);
    for(const row of documents)await tx.runAsync('INSERT INTO vectors(book,version,id,chapter,document) VALUES(?,?,?,?,?)',bundle.id,bundle.version,row.id,row.chapter_number,JSON.stringify(row));
    await tx.runAsync('INSERT OR REPLACE INTO models(book,version,model,metadata) VALUES(?,?,?,?)',bundle.id,bundle.version,index.model,JSON.stringify(metadata));
  });
}
export async function vectorSearch(bundle:Bundle,query:string,chapter?:number){
  if(!bundle.offline_index)return null;
  await installIndex(bundle);const db=await database();
  const model=await db.getFirstAsync<{metadata:string}>('SELECT metadata FROM models WHERE book=? AND version=?',bundle.id,bundle.version);
  if(!model)return null;
  const vector=queryVector(JSON.parse(model.metadata) as Omit<OfflineIndex,'documents'>,query);if(!vector)return [];
  const rows=chapter===undefined?await db.getAllAsync<{document:string}>('SELECT document FROM vectors WHERE book=? AND version=?',bundle.id,bundle.version):await db.getAllAsync<{document:string}>('SELECT document FROM vectors WHERE book=? AND version=? AND chapter=?',bundle.id,bundle.version,chapter);
  return rankVectors(rows.map(row=>JSON.parse(row.document) as VectorDocument),vector,chapter);
}
export async function removeIndex(book:string){const db=await database();await db.withExclusiveTransactionAsync(async tx=>{await tx.runAsync('DELETE FROM vectors WHERE book=?',book);await tx.runAsync('DELETE FROM models WHERE book=?',book);});}
export async function removeIndexVersion(book:string,version:string){const db=await database();await db.withExclusiveTransactionAsync(async tx=>{await tx.runAsync('DELETE FROM vectors WHERE book=? AND version=?',book,version);await tx.runAsync('DELETE FROM models WHERE book=? AND version=?',book,version);});await db.execAsync('PRAGMA wal_checkpoint(TRUNCATE);');}
