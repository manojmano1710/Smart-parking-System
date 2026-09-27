import os, cv2, numpy as np
BASE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(BASE,'sample_data','sample_parking.jpg')
def generate_sample_image():
    img=np.full((800,1200,3),145,np.uint8)
    for n in range(16):
        r,c=divmod(n,4); x1=60+c*270; y1=70+r*170; x2=x1+250; y2=y1+140
        cv2.rectangle(img,(x1,y1),(x2,y2),(220,220,220),3)
        if n%3==0:
            cv2.rectangle(img,(x1+25,y1+25),(x2-25,y2-25),(75,75,75),-1)
    os.makedirs(os.path.dirname(OUT),exist_ok=True); cv2.imwrite(OUT,img); return OUT
if __name__=='__main__': generate_sample_image()
