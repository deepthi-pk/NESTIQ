from fastapi import FastAPI,Depends,HTTPException,UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from .database import Base,engine,get_db
from .models import *
from .schemas import *
from .services.seed import seed
from .services.brain import UnifiedDeviceBrain,comfort
app=FastAPI(title='NESTIQ API'); app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def boot():
 Base.metadata.create_all(engine); db=next(get_db()); seed(db); db.close()
def out(d): return {'id':d.id,'name':d.name,'type':d.type,'room':d.room.name,'power':d.power,'brightness':d.brightness,'level':d.level,'last_changed':d.last_changed}
@app.get('/api/rooms')
def rooms(db:Session=Depends(get_db)): return [{'id':x.id,'name':x.name,'kind':x.kind} for x in db.query(Room).all()]
@app.get('/api/devices')
def devices(db:Session=Depends(get_db)): return [out(x) for x in db.query(Device).all()]
@app.patch('/api/devices/{id}')
def update(id:str,data:DeviceUpdate,db:Session=Depends(get_db)):
 d=db.get(Device,id)
 if not d: raise HTTPException(404,'Device not found')
 for k,v in data.model_dump(exclude_none=True).items(): setattr(d,k,v)
 d.last_changed=datetime.now(); db.add(DeviceStateHistory(device_id=d.id,state=data.model_dump(exclude_none=True))); db.add(TimelineEvent(title=f'{d.name} updated',description='Manual device adjustment.',type='device')); db.commit(); db.refresh(d); return out(d)
@app.get('/api/home-state')
def state(db:Session=Depends(get_db)): return {**comfort(db.query(Device).all()),'current_room':'Study Room','context':'Study','ai_confidence':92}
@app.post('/api/ai/intent')
def intent(data:IntentRequest,db:Session=Depends(get_db)):
 p=UnifiedDeviceBrain(db).plan(data.message)
 if not any(x in data.message.lower() for x in ['study','sleep','movie','living','comfortable','focus','prepare','room','what should']): p={'intent':'unknown','confidence':.35,'room':None,'actions':[],'reason':"I don't have enough context to safely determine that action.",'explanation':'No changes are proposed.'}
 db.add(AIInteraction(prompt=data.message,response=p)); db.commit(); return p
@app.post('/api/ai/recommendation')
def rec(db:Session=Depends(get_db)): return UnifiedDeviceBrain(db).recommendation()
@app.post('/api/simulation')
def simulation(data:ApplyRequest,db:Session=Depends(get_db)):
 cur=[]; pred=[]
 for a in data.actions:
  d=db.get(Device,a.device_id)
  if d: cur.append({'device':d.name,'value':d.brightness if a.action=='brightness' else d.level if a.action=='level' else ('ON' if d.power else 'OFF')}); pred.append({'device':d.name,'value':f'{a.value}%' if a.action=='brightness' else a.value if a.action=='level' else ('ON' if a.value else 'OFF')})
 return {'current':cur,'predicted':pred,'comfort':88,'note':'Preview only — NESTIQ has not changed your home.'}
@app.post('/api/simulation/apply')
def apply(data:ApplyRequest,db:Session=Depends(get_db)):
 for a in data.actions:
  d=db.get(Device,a.device_id)
  if not d or a.action not in ['power','brightness','level']: raise HTTPException(400,'Unsupported device action')
  setattr(d,a.action,a.value); d.last_changed=datetime.now(); db.add(TimelineEvent(title=f'{d.name} changed by NESTIQ',description='Approved AI action plan.',type='ai'))
 db.commit(); return {'ok':True}
@app.get('/api/memory')
def memory(db:Session=Depends(get_db)): return [{'id':o.id,'timestamp':o.timestamp,'room':o.room,'environment_type':o.environment_type,'detected_objects':o.detected_objects,'lighting_condition':o.lighting_condition,'notes':o.notes,'confidence':o.confidence} for o in db.query(HomeObservation).order_by(HomeObservation.timestamp.desc()).all()]
@app.post('/api/memory/search-object')
def search(data:ObjectSearch,db:Session=Depends(get_db)):
 q=data.query.lower().replace('where did i keep my','').replace('where is my','').replace('?','').strip(); x=db.query(ObjectObservation).filter(ObjectObservation.object_name.ilike(f'%{q}%')).order_by(ObjectObservation.observed_at.desc()).first(); return {'found':bool(x),'object':x.object_name.title() if x else q.title(),'location':x.location if x else None,'room':x.room if x else None,'observed_at':x.observed_at if x else None,'confidence':'High' if x else None}
@app.post('/api/memory/compare')
def compare(data:CompareRequest,db:Session=Depends(get_db)):
 a=db.get(HomeObservation,data.previous_id); b=db.get(HomeObservation,data.current_id)
 if not a or not b: raise HTTPException(404,'Observation not found')
 changes=[{'object':x.title(),'change':'Appeared' if x in b.detected_objects else 'No longer visible'} for x in set(a.detected_objects)^set(b.detected_objects)]+[{'object':x.title(),'change':'Position may have changed'} for x in set(a.detected_objects)&set(b.detected_objects) if x in ['notebook','backpack','lamp']]; return {'changes':changes,'label':'AI-detected changes based on saved observations'}
@app.post('/api/scan')
async def scan(file:UploadFile=File(...),db:Session=Depends(get_db)):
 objs=['desk','laptop','calculator','notebook','lamp']; o=HomeObservation(room='Study Room',environment_type='study',detected_objects=objs,lighting_condition='low',notes='DEMO MODE: predefined study scan.',confidence=.91); db.add(o); db.flush()
 for x in ['calculator','notebook']: db.add(ObjectObservation(object_name=x,location='Study Desk',room='Study Room',confidence=.91,observation_id=o.id))
 db.add(TimelineEvent(title='Study environment scanned',description='Demo-mode observation saved to Home Memory.',type='scan')); db.commit(); return {'demo_mode':True,'room':'Study Room','environment':'Study','objects':objs,'lighting':'Low','confidence':.91,'observation_id':o.id}
@app.get('/api/timeline')
def timeline(db:Session=Depends(get_db)): return [{'id':e.id,'timestamp':e.timestamp,'title':e.title,'description':e.description,'type':e.type} for e in db.query(TimelineEvent).order_by(TimelineEvent.timestamp.desc()).all()]
@app.get('/api/automations')
def autos(db:Session=Depends(get_db)): return [{'id':a.id,'name':a.name,'trigger':a.trigger,'actions':a.actions,'approved':a.approved,'explanation':a.explanation} for a in db.query(Automation).all()]
@app.post('/api/automations')
def create_auto(data:AutomationCreate,db:Session=Depends(get_db)):
 a=Automation(**data.model_dump()); db.add(a); db.commit(); db.refresh(a); return {'id':a.id,'name':a.name}
@app.post('/api/automations/{id}/approve')
def approve(id:int,db:Session=Depends(get_db)):
 a=db.get(Automation,id)
 if not a: raise HTTPException(404,'Automation not found')
 a.approved=True; db.add(TimelineEvent(title=f'{a.name} approved',description='User approved learned automation.',type='automation')); db.commit(); return {'ok':True}
@app.get('/api/anomalies')
def anomalies(): return [{'title':'Unusual activity','message':"This activity differs from the home's learned Study Room pattern.",'time':'Outside usual 5–9 PM baseline'}]
@app.post('/api/demo/reset')
def reset(db:Session=Depends(get_db)): seed(db,True); return {'ok':True}
@app.post('/api/demo/event')
def event(data:DemoEvent,db:Session=Depends(get_db)): db.add(RoutineEvent(event_type=data.event_type,room=data.room,details='Demo control')); db.add(TimelineEvent(title=data.event_type,description=f'{data.room} simulated through demo controls.',type='demo')); db.commit(); return {'ok':True}
