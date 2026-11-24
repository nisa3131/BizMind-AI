import React, {useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';
const API='/api/v1';
function App(){
 const [token,setToken]=useState(localStorage.getItem('bizmind_token')||'');
 const [business,setBusiness]=useState(''); const [invite,setInvite]=useState(''); const [email,setEmail]=useState('');
 const [password,setPassword]=useState('');const [question,setQuestion]=useState('');
 const [answer,setAnswer]=useState('');const [sources,setSources]=useState<any[]>([]);
 const [docs,setDocs]=useState<any[]>([]);const [stats,setStats]=useState<any>(null);
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState('');const [mode,setMode]=useState('');
 async function request(path:string,options:RequestInit={}){
  const response=await fetch(API+path,{...options,headers:{...(options.body instanceof FormData?{}:{'Content-Type':'application/json'}),...(token?{Authorization:'Bearer '+token}:{}),...options.headers}});
  const data=await response.json();if(!response.ok)throw new Error(data.detail||'Request failed');return data;
 }
 async function auth(mode:'login'|'signup'){try{
  const data=await request('/auth/'+mode,{method:'POST',body:JSON.stringify(mode==='signup'?{business_name:business,email,password,invite_code:invite}:{email,password})});
  localStorage.setItem('bizmind_token',data.access_token);setToken(data.access_token);setMessage('Signed in');
 }catch(e){setMessage(String(e))}}
 async function upload(file:File){setBusy('upload');setMessage('Indexing document… First upload may download the embedding model.');const form=new FormData();form.append('file',file);try{await request('/documents',{method:'POST',body:form});setMessage('Document indexed successfully');await loadDocs()}catch(e){setMessage(String(e))}finally{setBusy('')}}
 async function loadDocs(){try{setDocs(await request('/documents'))}catch(e){setMessage(String(e))}}
 async function ask(){setBusy('ask');setAnswer('');setSources([]);setMode('');setMessage('');try{const data=await request('/chat',{method:'POST',body:JSON.stringify({question})});setAnswer(data.answer);setSources(data.citations);setMode(data.answer_mode)}catch(e){setMessage(String(e))}finally{setBusy('')}}
 async function analytics(){try{setStats(await request('/analytics'))}catch(e){setMessage(String(e))}}
 return <main><header className="hero"><small>DOCUMENT INTELLIGENCE PLATFORM</small><h1>BizMind AI</h1><p>Secure, tenant-scoped document search and customer support.</p></header>
 {message&&<p role="status">{message}</p>}
 {!token?<section><h2>Business owner access</h2><input placeholder="Business name (for signup)" value={business} onChange={e=>setBusiness(e.target.value)}/><input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/><input type="password" placeholder="Password (12+ characters)" value={password} onChange={e=>setPassword(e.target.value)}/><input type="password" aria-label="Demo invite code" placeholder="Demo invite code (if required)" value={invite} onChange={e=>setInvite(e.target.value)}/><button onClick={()=>auth('signup')}>Create account</button><button onClick={()=>auth('login')}>Sign in</button></section>:<>
 <button onClick={()=>{localStorage.removeItem('bizmind_token');setToken('');setDocs([]);setStats(null);setAnswer('');setSources([]);setQuestion('');setMode('');setPassword('');setMessage('')}}>Sign out</button>
 <section><h2>Knowledge base</h2><input aria-label="Upload PDF or text FAQ" type="file" disabled={!!busy} accept=".pdf,.txt,application/pdf,text/plain" onChange={e=>e.target.files?.[0]&&upload(e.target.files[0])}/><button onClick={loadDocs}>Refresh documents</button>{docs.map(d=><p key={d.id}>{d.filename}</p>)}</section>
 <section><h2>Ask your documents</h2><textarea value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ask a question about your uploaded documents"/><button onClick={ask} disabled={!!busy||!question.trim()}>{busy==='ask'?'Searching documents…':'Ask BizMind'}</button>{mode&&<p className="mode">Answer mode: {mode==='generated'?'Hosted generation':mode==='extractive'?'Local cited excerpts':'No sources found'}</p>}<pre>{answer}</pre>{sources.map((s,i)=><small key={i}>[{i+1}] {s.source} · chunk {s.chunk}<br/></small>)}</section>
 <section><h2>Analytics</h2><button onClick={analytics}>Refresh analytics</button>{stats&&<div className="grid"><div className="metric"><small>Total queries</small><strong>{stats.total_queries}</strong></div><div className="metric"><small>Average latency</small><strong>{stats.average_latency_ms} ms</strong></div></div>}</section></>}
 </main>
}createRoot(document.getElementById('root')!).render(<App/>);
