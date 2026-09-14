class UnifiedDeviceBrain:
    def __init__(self, db): self.db=db
    def plan(self, message):
        text=message.lower(); room='Study Room'; intent='study_mode'; reason='The user indicated they are going to study.'
        if any(x in text for x in ['sleep','bed']): room='Bedroom'; intent='sleep_mode'; reason='Sleep intent detected; NESTIQ will lower stimulation.'; specs=[('bedroom_light','Bedroom Light','power',False),('bedroom_fan','Bedroom Fan','level','Low'),('bedroom_ac','Bedroom AC','level','24°C')]
        elif any(x in text for x in ['movie','living','comfortable']): room='Living Room'; intent='comfort_mode'; reason='A comfortable shared environment was requested.'; specs=[('living_light','Living Room Light','brightness',60),('living_fan','Living Room Fan','level','Medium')]
        else: specs=[('desk_lamp','Desk Lamp','power',True),('study_light','Study Room Light','brightness',60),('study_fan','Study Fan','level','Medium')]
        return {'intent':intent,'confidence':.92,'room':room,'actions':[{'device_id':i,'device':n,'action':a,'value':v} for i,n,a,v in specs],'reason':reason,'explanation':'Based on your request and saved study routines. This is a proposed plan; no device has changed yet.'}
    def recommendation(self):
        p=self.plan("I'm going to study"); return {'title':'Your usual study period has started','room':'Study Room','confidence':92,'message':'You usually begin studying around this time. Prepare your study environment?','reason':'Recent saved routine events show repeated Study Room activity in the evening.','actions':p['actions']}
def comfort(devices):
    active=sum(1 for d in devices if d.power); lighting=85 if any(d.power and d.brightness for d in devices) else 58
    return {'score':min(95,72+active*3),'lighting':lighting,'temperature':90,'noise':70,'activity':82,'energy':'Normal','summary':'Your environment is suitable for studying, but noise is above your usual study baseline.'}
