from __future__ import annotations
import os
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from sqlalchemy import Boolean, DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from app.outreach import build_outreach_draft

DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./driftless.db')
JWT_SECRET=os.getenv('DRIFTLESS_JWT_SECRET')
if not JWT_SECRET: raise RuntimeError('DRIFTLESS_JWT_SECRET must be set')
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'; id:Mapped[int]=mapped_column(Integer,primary_key=True); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(255)); active:Mapped[bool]=mapped_column(Boolean,default=True)
class Employer(Base):
    __tablename__='employers'; id:Mapped[int]=mapped_column(Integer,primary_key=True); name:Mapped[str]=mapped_column(String(255),index=True); location:Mapped[str]=mapped_column(String(255),default=''); status:Mapped[str]=mapped_column(String(40),default='Prospect'); notes:Mapped[str]=mapped_column(Text,default='')
class Candidate(Base):
    __tablename__='candidates'; id:Mapped[int]=mapped_column(Integer,primary_key=True); name:Mapped[str]=mapped_column(String(255)); skills:Mapped[str]=mapped_column(Text,default=''); location:Mapped[str]=mapped_column(String(255),default=''); available:Mapped[bool]=mapped_column(Boolean,default=True); notes:Mapped[str]=mapped_column(Text,default='')
class Search(Base):
    __tablename__='searches'; id:Mapped[int]=mapped_column(Integer,primary_key=True); title:Mapped[str]=mapped_column(String(255)); employer_id:Mapped[int]=mapped_column(Integer,index=True); requirements:Mapped[str]=mapped_column(Text,default=''); location:Mapped[str]=mapped_column(String(255),default=''); status:Mapped[str]=mapped_column(String(40),default='Open'); created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
class Contact(Base):
    __tablename__='contacts'; id:Mapped[int]=mapped_column(Integer,primary_key=True); employer_slug:Mapped[str]=mapped_column(String(255),index=True); name:Mapped[str]=mapped_column(String(255)); title:Mapped[str]=mapped_column(String(255)); source_url:Mapped[str]=mapped_column(String(1000)); verified_at:Mapped[str]=mapped_column(String(40)); email:Mapped[str|None]=mapped_column(String(255),nullable=True); phone:Mapped[str|None]=mapped_column(String(80),nullable=True); status:Mapped[str]=mapped_column(String(40),default='verified'); notes:Mapped[str]=mapped_column(Text,default='')
Base.metadata.create_all(engine)
app=FastAPI(title='Driftless Workforce API',version='1.0.0')
oauth=OAuth2PasswordBearer(tokenUrl='/auth/token'); hasher=PasswordHash.recommended()
def db():
    s=SessionLocal()
    try:yield s
    finally:s.close()
def current_user(token:str=Depends(oauth),s:Session=Depends(db)):
    try:payload=jwt.decode(token,JWT_SECRET,algorithms=['HS256']); uid=int(payload['sub'])
    except Exception:raise HTTPException(status_code=401,detail='Invalid authentication token')
    user=s.get(User,uid)
    if not user or not user.active:raise HTTPException(status_code=401,detail='Inactive user')
    return user
@app.get('/health')
def health():return {'ok':True,'service':'driftless-api'}
@app.post('/auth/register')
def register(email:str,password:str,s:Session=Depends(db)):
    if len(password)<12:raise HTTPException(400,'Password must be at least 12 characters')
    if s.scalar(select(User).where(User.email==email.lower())):raise HTTPException(409,'Account already exists')
    u=User(email=email.lower(),password_hash=hasher.hash(password));s.add(u);s.commit();return {'id':u.id,'email':u.email}
@app.post('/auth/token')
def token(form:OAuth2PasswordRequestForm=Depends(),s:Session=Depends(db)):
    u=s.scalar(select(User).where(User.email==form.username.lower()))
    if not u or not hasher.verify(form.password,u.password_hash):raise HTTPException(status_code=401,detail='Incorrect email or password')
    exp=datetime.now(timezone.utc)+timedelta(hours=8);return {'access_token':jwt.encode({'sub':str(u.id),'exp':exp},JWT_SECRET,algorithm='HS256'),'token_type':'bearer'}
@app.get('/prospects')
def prospects(minimum_score:int=0, priority:str='', limit:int=100, _:User=Depends(current_user)):
    """Return the current Scout queue from generated employer intelligence."""
    path=Path(__file__).resolve().parents[1]/'data'/'employer_opportunities.json'
    if not path.exists(): raise HTTPException(503,'Employer intelligence dataset is not available')
    try: records=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError) as exc: raise HTTPException(500,'Employer intelligence dataset could not be read') from exc
    queue=[]
    for item in records:
        score=int(item.get('score',0))
        if score < max(0,minimum_score): continue
        if priority and str(item.get('priority','')).lower()!=priority.lower(): continue
        queue.append({'employer':item.get('employer',''),'slug':item.get('slug',''),'score':score,'priority':item.get('priority','Low'),'opening_count':int(item.get('opening_count',0)),'verified_opening_count':int(item.get('verified_opening_count',0)),'locations':item.get('locations',[]),'industries':item.get('industries',[]),'target_roles':item.get('target_roles',[]),'decision_maker_roles':item.get('decision_maker_roles',[]),'contact_path':item.get('contact_path',''),'outreach_angle':item.get('outreach_angle',''),'evidence':item.get('evidence',[]),'jobs':item.get('jobs',[]),'status':'new','contact':None,'outreach':{'state':'not_started','next_action':None}})
    queue.sort(key=lambda x:(-x['score'],-x['verified_opening_count'],-x['opening_count'],x['slug']))
    return queue[:max(1,min(limit,500))]

@app.get('/prospects/{slug}/contacts')
def prospect_contacts(slug:str,_:User=Depends(current_user),s:Session=Depends(db)):
    return s.scalars(select(Contact).where(Contact.employer_slug==slug).order_by(Contact.verified_at.desc(),Contact.name)).all()

@app.post('/prospects/{slug}/contacts')
def add_prospect_contact(slug:str,name:str,title:str,source_url:str,verified_at:str,email:Optional[str]=None,phone:Optional[str]=None,notes:str='',_:User=Depends(current_user),s:Session=Depends(db)):
    if not name.strip() or not title.strip() or not source_url.strip() or not verified_at.strip():
        raise HTTPException(400,'name, title, source_url, and verified_at are required')
    c=Contact(employer_slug=slug,name=name.strip(),title=title.strip(),source_url=source_url.strip(),verified_at=verified_at.strip(),email=email.strip() if email else None,phone=phone.strip() if phone else None,notes=notes.strip())
    s.add(c);s.commit();s.refresh(c);return c

@app.delete('/prospects/{slug}/contacts/{contact_id}')
def delete_prospect_contact(slug:str,contact_id:int,_:User=Depends(current_user),s:Session=Depends(db)):
    c=s.get(Contact,contact_id)
    if not c or c.employer_slug!=slug: raise HTTPException(404,'Contact not found')
    s.delete(c);s.commit();return {'deleted':True,'contact_id':contact_id}

@app.post('/prospects/{slug}/outreach/draft')
def draft_prospect_outreach(slug:str,contact_id:int,sender_name:str='Casey',_:User=Depends(current_user),s:Session=Depends(db)):
    path=Path(__file__).resolve().parents[1]/'data'/'employer_opportunities.json'
    if not path.exists(): raise HTTPException(503,'Employer intelligence dataset is not available')
    try: records=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError) as exc: raise HTTPException(500,'Employer intelligence dataset could not be read') from exc
    prospect=next((item for item in records if item.get('slug')==slug),None)
    if not prospect: raise HTTPException(404,'Prospect not found')
    contact=s.get(Contact,contact_id)
    if not contact or contact.employer_slug!=slug: raise HTTPException(404,'Verified contact not found')
    try:
        return build_outreach_draft(prospect,{'name':contact.name,'title':contact.title,'source_url':contact.source_url},sender_name)
    except ValueError as exc: raise HTTPException(400,str(exc)) from exc

@app.get('/employers')
def employers(_:User=Depends(current_user),s:Session=Depends(db)):return s.scalars(select(Employer).order_by(Employer.name)).all()
@app.post('/employers')
def create_employer(name:str,location:str='',notes:str='',_:User=Depends(current_user),s:Session=Depends(db)):
    e=Employer(name=name,location=location,notes=notes);s.add(e);s.commit();s.refresh(e);return e
@app.get('/candidates')
def candidates(_:User=Depends(current_user),s:Session=Depends(db)):return s.scalars(select(Candidate).order_by(Candidate.name)).all()
@app.post('/candidates')
def create_candidate(name:str,skills:str='',location:str='',available:bool=True,notes:str='',_:User=Depends(current_user),s:Session=Depends(db)):
    c=Candidate(name=name,skills=skills,location=location,available=available,notes=notes);s.add(c);s.commit();s.refresh(c);return c
@app.get('/searches')
def searches(_:User=Depends(current_user),s:Session=Depends(db)):return s.scalars(select(Search).order_by(Search.created_at.desc())).all()
@app.post('/searches')
def create_search(title:str,employer_id:int,requirements:str='',location:str='',_:User=Depends(current_user),s:Session=Depends(db)):
    if not s.get(Employer,employer_id):raise HTTPException(404,'Employer not found')
    r=Search(title=title,employer_id=employer_id,requirements=requirements,location=location);s.add(r);s.commit();s.refresh(r);return r
@app.get('/searches/{search_id}/matches')
def matches(search_id:int,limit:int=20,_:User=Depends(current_user),s:Session=Depends(db)):
    r=s.get(Search,search_id)
    if not r:raise HTTPException(404,'Search not found')
    req={x for x in r.requirements.lower().replace(',',' ').split() if len(x)>1};out=[]
    for c in s.scalars(select(Candidate).where(Candidate.available==True)):
        skills={x for x in c.skills.lower().replace(',',' ').split() if len(x)>1};overlap=sorted(req&skills);score=min(100,round(len(overlap)/len(req)*70) if req else 0)+(20 if not r.location or c.location.lower()==r.location.lower() else 0)+10
        out.append({'candidate_id':c.id,'candidate_name':c.name,'score':min(100,score),'matched_skills':overlap})
    return sorted(out,key=lambda x:x['score'],reverse=True)[:max(1,min(limit,100))]
