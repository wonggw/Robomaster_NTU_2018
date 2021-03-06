import numpy as np 
from math import sqrt

def get_v_and_shoot(valid_coord,pid,img):
	if valid_coord != []:
		dist = [a[0]*a[0]+a[1]*a[1] for a in valid_coord]
		selected = np.argmax(-np.array(dist))
		width = valid_coord[selected][2]
		height = valid_coord[selected][3]
		x = valid_coord[selected][0]
		y = valid_coord[selected][1]
		x_bias = 2.1*sqrt(np.log(width * height)) + 1
		y_bias = 3.9*sqrt(np.log(width * height)) + 2.5
		
		# adjust with offset
		x_offset = x - img.shape[1]//2 - x_bias
		y_offset = y - img.shape[0]//2 - y_bias
		
		# Shooting logic
		if abs(x_offset) < 10 and abs(y_offset) < 8  :
			pid.eval([x_offset, y_offset]) # must update pid to maintain the time
			v_2 = 0
			v_1 = 0
			shoot = 4
		else:
			v_2, v_1= pid.eval([x_offset, y_offset])
			shoot = 0
		return v_1,v_2,shoot
	return 0,0,0

def normalize_uwb(w,h,ang):
	w = (w+5)//10
	h = (h+5)//10
	# change the bias while testing 
	ang_bias = -3
	w_offset = 0
	h_offset = -2
	ang = (ang+450)//900 + ang_bias
	if ang<0: 
		ang += 40
	return w+w_offset,h+h_offset,ang


# encoder and decoder for communication between two robots
def encode_whang(w,h,ang):
	whang = np.int16([w,h,ang])
	encoded = whang.tobytes()
	return encoded

def decode_whang(whang):
	whang = np.frombuffer(whang,dtype=np.int16)
	w,h,ang = whang[0],whang[1],whang[2]
	return w,h,ang
