from __future__ import annotations
import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Integer, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import jwt
from passlib.context import CryptContext

DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./driftless.db')
SECRET=os.getenv('DRIFTLESS_JWT_SECRET','change-me-in-production')
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); bearer=HTTPBearer()
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'; id:Mapped[int]=mapped_column(primary_key=True); email:Mapped[str]=mapped_column(String(255),unique=True,index=True); password_hash:Mapped[str]=mapped_column(String(255))
class Employer(Base):
    __tablename__='employers'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(255),index=True); status:Mapped[str]=mapped_column(String(50),default='PROSPECT'); notes:Mapped[str]=mapped_column(Text,default='')
class Candidate(Base):
    __tablename__='candidates'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(255)); skills:Mapped[str]=mapped_column(Text,default=''); location:Mapped[str]=mapped_column(String(255),default=''); availability:Mapped[str]=mapped_column(String(255),default='')
class Search(Base):
    __tablename__='searches'; id:Mapped[int]=mapped_column(primary_key=True); employer_id:Mapped[int]; title:Mapped[str]=mapped_column(String(255)); status:Mapped[str]=mapped_column(String(50),default='OPEN'); requirements:Mapped[str]=mapped_column(Text,default='')
Base.metadata.create_all(engine)
app=FastAPI(title='Driftless Workforce API',version='1.0.0')
class Auth(BaseModel): email:str; password:str=Field(min_length=10)
class EmployerIn(BaseModel): name:str; status:str='PROSPECT'; notes:str=''
class CandidateIn(BaseModel): name:str; skills:list[str]=[]; location:str=''; availability:str=''
class SearchIn(BaseModel): employer_id:int; title:str; status:str='OPEN'; requirements:list[str]=[]
def token_for(user): return jwt.encode({'sub':str(user.id),'exp':datetime.now(timezone.utc)+timedelta(hours=8)},SECRET,algorithm='HS256')
def current_user(creds:HTTPAuthorizationCredentials=Depends(bearer)):
    try: payload=jwt.decode(creds.credentials,SECRET,algorithms=['HS256']); uid=int(payload['sub'])
    except Exception: raise HTTPException(401,'Invalid authentication token')
    with Session(engine) as db: user=db.get(User,uid)
    if not user: raise HTTPException(401,'User not found')
    return user
@app.get('/health')
def health(): return {'status':'ok','service':'driftless-workforce-api'}
@app.post('/auth/register')
def register(data:Auth):
    with Session(engine) as db:
        if db.query(User).filter_by(email=data.email.lower()).first(): raise HTTPException(409,'Email already registered')
        u=User(email=data.email.lower(),password_hash=pwd.hash(data.password)); db.add(u); db.commit(); db.refresh(u); return {'token':token_for(u)}
@app.post('/auth/login')
def login(data:Auth):
    with Session(engine) as db:
        u=db.query(User).filter_by(email=data.email.lower()).first()
        if not u or not pwd.verify(data.password,u.password_hash): raise HTTPException(401,'Invalid credentials')
        return {'token':token_for(u)}
@app.get('/employers')
def employers(user=Depends(current_user)):
    with Session(engine) as db: return [{'id':e.id,'name':e.name,'status':e.status,'notes':e.notes} for e in db.query(Employer).order_by(Employer.name).all()]
@app.post('/employers')
def add_employer(data:EmployerIn,user=Depends(current_user)):
    with Session(engine) as db: e=Employer(**data.model_dump()); db.add(e); db.commit(); db.refresh(e); return {'id':e.id,**data.model_dump()}
@app.get('/candidates')
def candidates(user=Depends(current_user)):
    with Session(engine) as db: return [{'id':c.id,'name':c.name,'skills':c.skills.split(',') if c.skills else [],'location':c.location,'availability':c.availability} for c in db.query(Candidate).all()]
@app.post('/candidates')
def add_candidate(data:CandidateIn,user=Depends(current_user)):
    with Session(engine) as db: c=Candidate(name=data.name,skills=','.join(data.skills),location=data.location,availability=data.availability); db.add(c); db.commit(); db.refresh(c); return {'id':c.id,**data.model_dump()}
@app.post('/searches')
def add_search(data:SearchIn,user=Depends(current_user)):
    with Session(engine) as db:
        if not db.get(Employer,data.employer_id): raise HTTPException(404,'Employer not found')
        s=Search(employer_id=data.employer_id,title=data.title,status=data.status,requirements=','.join(data.requirements)); db.add(s); db.commit(); db.refresh(s); return {'id':s.id,**data.model_dump()}
@app.get('/searches')
def searches(user=Depends(current_user)):
    with Session(engine) as db: return [{'id':s.id,'employer_id':s.employer_id,'title':s.title,'status':s.status,'requirements':s.requirements.split(',') if s.requirements else []} for s in db.query(Search).all()]
@app.get('/searches/{search_id}/matches')
def matches(search_id:int,user=Depends(current_user)):
    with Session(engine) as db:
        s=db.get(Search,search_id)
        if not s: raise HTTPException(404,'Search not found')
        req={x.strip().lower() for x in s.requirements.split(',') if x.strip()}; rows=[]
        for c in db.query(Candidate).all():
            skills={x.strip().lower() for x in c.skills.split(',') if x.strip()}; overlap=len(req&skills); score=round(overlap/len(req)*100) if req else 0
            rows.append({'candidate_id':c.id,'candidate':c.name,'score':score,'matched_skills':sorted(req&skills)})
        return sorted(rows,key=lambda x:(-x['score'],x['candidate']))
