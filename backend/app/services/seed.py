from datetime import datetime, timedelta
from ..models import Room,Device,HomeObservation,ObjectObservation,RoutineEvent,TimelineEvent,Automation
def seed(db, force=False):
 if force:
  for m in [ObjectObservation,HomeObservation,Device,Room,RoutineEvent,TimelineEvent,Automation]: db.query(m).delete()
 if db.query(Room).count(): return
 rooms=[Room(name='Bedroom',kind='bedroom'),Room(name='Living Room',kind='living'),Room(name='Study Room',kind='study')]; db.add_all(rooms); db.flush(); ids={r.name:r.id for r in rooms}
 specs=[('bedroom_light','Bedroom Light','light','Bedroom',False,30,None),('bedroom_fan','Bedroom Fan','fan','Bedroom',True,None,'Low'),('bedroom_ac','Bedroom AC','ac','Bedroom',True,None,'24°C'),('living_light','Living Room Light','light','Living Room',True,70,None),('living_fan','Living Room Fan','fan','Living Room',True,None,'Medium'),('tv','TV','tv','Living Room',False,None,None),('smart_plug','Smart Plug','plug','Living Room',True,None,None),('desk_lamp','Desk Lamp','light','Study Room',False,0,None),('study_light','Study Room Light','light','Study Room',True,100,None),('study_fan','Study Fan','fan','Study Room',True,None,'Low')]
 db.add_all([Device(id=i,name=n,type=t,room_id=ids[r],power=p,brightness=b,level=l) for i,n,t,r,p,b,l in specs]); now=datetime.now()
 data=[('Study Room','study',['desk','laptop','calculator','notebook','lamp','backpack'],'low'),('Living Room','movie',['tv','sofa','remote','headphones'],'dim'),('Bedroom','rest',['bed','charger','lamp'],'low'),('Study Room','study',['desk','laptop','notebook','charger'],'normal'),('Living Room','relax',['sofa','backpack','headphones'],'warm')]
 for i,(room,env,objs,light) in enumerate(data):
  o=HomeObservation(timestamp=now-timedelta(hours=(5-i)*3),room=room,environment_type=env,detected_objects=objs,lighting_condition=light,notes='Seeded NESTIQ observation',confidence=.9); db.add(o); db.flush()
  loc={'calculator':'Study Desk','notebook':'Study Desk','charger':'Bedside Table','backpack':'Study Chair','headphones':'Living Room Sofa'}
  for x in objs:
   if x in loc: db.add(ObjectObservation(object_name=x,location=loc[x],room=room,observed_at=o.timestamp,confidence=.9,observation_id=o.id))
 for i in range(15): db.add(TimelineEvent(timestamp=now-timedelta(minutes=i*22),title=['Study environment detected','Desk Lamp activated','User entered Study Room','Focus session started'][i%4],description='Recorded by the NESTIQ Home Brain.',type='activity'))
 for i in range(12): db.add(RoutineEvent(timestamp=now-timedelta(days=i%4,hours=2),event_type=['Entered Study Room','Desk Lamp ON','Laptop active'][i%3],room='Study Room',details='Evening study pattern'))
 db.add(Automation(name='Study Mode',trigger='Weekday evenings in Study Room',actions=[{'device_id':'desk_lamp','action':'power','value':True},{'device_id':'study_light','action':'brightness','value':60},{'device_id':'study_fan','action':'level','value':'Medium'}],approved=False,explanation='Repeated Study Room patterns were observed during evening hours.')); db.commit()
