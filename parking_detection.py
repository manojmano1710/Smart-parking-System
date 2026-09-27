import os, cv2, numpy as np
DEFAULT_OCCUPANCY_THRESHOLD=0.22
SLOTS=[]
for n in range(16):
    r,c=divmod(n,4); x1=60+c*270; y1=70+r*170; SLOTS.append((f'Slot {n+1:02d}',x1,y1,x1+250,y1+140))
def process_parking_image(path, threshold=DEFAULT_OCCUPANCY_THRESHOLD):
    img=cv2.imread(path)
    if img is None: raise ValueError('Invalid image.')
    img=cv2.resize(img,(1200,800)); details=[]
    for name,x1,y1,x2,y2 in SLOTS:
        crop=img[y1:y2,x1:x2]; gray=cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY); edges=cv2.Canny(gray,60,150)
        ratio=float(np.mean(edges>0))
        occupied=ratio>threshold
        color=(0,0,255) if occupied else (0,180,0)
        cv2.rectangle(img,(x1,y1),(x2,y2),color,3); cv2.putText(img,name,(x1+8,y1+25),cv2.FONT_HERSHEY_SIMPLEX,.55,color,2)
        details.append({'slot_number':name,'status':'OCCUPIED' if occupied else 'AVAILABLE','pixel_ratio':round(ratio,4),'x1':x1,'y1':y1,'x2':x2,'y2':y2})
    occ=sum(d['status']=='OCCUPIED' for d in details); total=len(details)
    summary={'total_slots':total,'occupied_slots':occ,'available_slots':total-occ,'occupancy_percentage':round(occ/total*100,2)}
    out=os.path.join(os.path.dirname(path),'processed','processed_'+os.path.basename(path)); os.makedirs(os.path.dirname(out),exist_ok=True); cv2.imwrite(out,img)
    return {'summary':summary,'slot_details':details,'processed_filename':out}
