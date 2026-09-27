import csv,io,os,sqlite3
from datetime import datetime
import cv2
from fastapi import FastAPI,File,Form,UploadFile,Header,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,StreamingResponse
from auth import *
from database import *
from models import *
from parking_detection import *
BASE=os.path.dirname(os.path.abspath(__file__)); UP=os.path.join(BASE,'uploads'); SAMPLE=os.path.join(BASE,'sample_data','sample_parking.jpg'); os.makedirs(UP,exist_ok=True)
app=FastAPI(title='Smart Parking System API'); app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup(): init_database()
def current_user(authorization: str|None=Header(None)):
    token=authorization.split(' ',1)[1] if authorization and authorization.lower().startswith('bearer ') else None; u=get_username_from_token(token)
    if not u: raise HTTPException(401,'Authentication required')
    c=get_connection(); r=c.execute('SELECT * FROM users WHERE username=?',(u,)).fetchone(); c.close(); return row_to_dict(r)
@app.get('/')
def root(): return {'success':True,'message':'Smart Parking System API is running'}
@app.post('/api/login')
def login(p:LoginRequest):
    c=get_connection(); r=c.execute('SELECT * FROM users WHERE username=?',(p.username,)).fetchone(); c.close()
    if not r or not verify_password(p.password,r['password']): raise HTTPException(401,'Invalid username or password')
    return {'success':True,'token':create_token(p.username),'user':{'id':r['id'],'username':r['username'],'full_name':r['full_name'],'email':r['email'],'phone':r['phone']}}
@app.post('/api/register')
def register(p:RegisterRequest):
    c=get_connection()
    try: c.execute('INSERT INTO users(username,password,full_name,email) VALUES(?,?,?,?)',(p.username,hash_password(p.password),p.full_name,p.email)); c.commit(); return {'success':True,'message':'Registration successful'}
    except sqlite3.IntegrityError: raise HTTPException(400,'Username already exists')
    finally: c.close()
@app.post('/api/detect-parking')
async def detect_parking(file:UploadFile=File(...),occupancy_threshold:float=Form(DEFAULT_OCCUPANCY_THRESHOLD),user:dict=Depends(current_user)):
    data=await file.read(); name=f'{datetime.now().strftime("%Y%m%d_%H%M%S")}_{file.filename or "parking.jpg"}'; path=os.path.join(UP,name); open(path,'wb').write(data)
    result=process_parking_image(path,occupancy_threshold); s=result['summary']; now=datetime.now().strftime('%Y-%m-%d %H:%M:%S'); c=get_connection()
    c.execute('INSERT INTO detection_history(total_slots,occupied_slots,available_slots,occupancy_percentage,detection_time) VALUES(?,?,?,?,?)',(s['total_slots'],s['occupied_slots'],s['available_slots'],s['occupancy_percentage'],now))
    for d in result['slot_details']: c.execute('UPDATE parking_slots SET status=?,pixel_ratio=?,last_updated=? WHERE slot_number=?',(d['status'],d['pixel_ratio'],now,d['slot_number']))
    c.commit(); c.close(); return {'success':True,**s,'slot_details':result['slot_details'],'processed_image':'/api/processed/'+os.path.basename(result['processed_filename']),'detection_time':now}
@app.get('/api/processed/{name}')
def processed(name:str): return FileResponse(os.path.join(UP,'processed',name))
@app.get('/api/sample-image')
def sample_image():
    if not os.path.exists(SAMPLE): __import__('generate_sample').generate_sample_image()
    return FileResponse(SAMPLE,media_type='image/jpeg')
@app.get('/api/parking-status')
def parking_status(user=Depends(current_user)):
    c=get_connection(); latest=c.execute('SELECT * FROM detection_history ORDER BY id DESC LIMIT 1').fetchone(); slots=c.execute('SELECT * FROM parking_slots ORDER BY id').fetchall(); c.close(); sl=[row_to_dict(x) for x in slots]
    if latest: d=row_to_dict(latest); return {'success':True,**d,'slots':sl}
    total=len(sl); occ=sum(x['status']=='OCCUPIED' for x in sl); return {'success':True,'total_slots':total,'occupied_slots':occ,'available_slots':total-occ,'occupancy_percentage':round(occ/total*100,2),'slots':sl}
@app.get('/api/parking-slots')
def parking_slots(user=Depends(current_user)):
    c=get_connection(); rows=c.execute('SELECT * FROM parking_slots ORDER BY id').fetchall(); c.close(); return {'success':True,'slots':[row_to_dict(x) for x in rows]}
@app.get('/api/reports')
def reports(user=Depends(current_user)):
    c=get_connection(); rows=c.execute('SELECT * FROM detection_history ORDER BY id DESC').fetchall(); c.close(); return {'success':True,'history':[row_to_dict(x) for x in rows]}
@app.get('/api/reports/csv')
def reports_csv(user=Depends(current_user)):
    c=get_connection(); rows=c.execute('SELECT * FROM detection_history ORDER BY id DESC').fetchall(); c.close(); out=io.StringIO(); w=csv.writer(out); w.writerow(['ID','Total Slots','Occupied Slots','Available Slots','Occupancy Percentage','Detection Time']); [w.writerow([r['id'],r['total_slots'],r['occupied_slots'],r['available_slots'],r['occupancy_percentage'],r['detection_time']]) for r in rows]; out.seek(0); return StreamingResponse(iter([out.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=parking_report.csv'})
@app.get('/api/profile')
def profile(user=Depends(current_user)): return {'success':True,'user':user}
@app.put('/api/profile')
def update_profile(p:ProfileUpdateRequest,user=Depends(current_user)):
    c=get_connection(); c.execute('UPDATE users SET full_name=?,email=?,phone=? WHERE id=?',(p.full_name,p.email,p.phone,user['id'])); c.commit(); c.close(); return {'success':True,'message':'Profile updated'}
@app.post('/api/change-password')
def change_password(p:PasswordChangeRequest,user=Depends(current_user)):
    if p.new_password!=p.confirm_password: raise HTTPException(400,'Passwords do not match')
    if not verify_password(p.current_password,user['password']): raise HTTPException(400,'Current password is incorrect')
    c=get_connection(); c.execute('UPDATE users SET password=? WHERE id=?',(hash_password(p.new_password),user['id'])); c.commit(); c.close(); return {'success':True,'message':'Password changed'}
