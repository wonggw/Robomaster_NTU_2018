import tensorflow as tf 
import model as M 
import cv2
import numpy as np

BSIZE = 128
BLACK = (0,0,0)

x =65
y = 0

def PickSevenSegment(BSIZE):
	img = []
	y_label = []
	for i in range(BSIZE):
		pick_digit = np.random.randint(1,11)
		digit_label = np.zeros((11,), dtype=int)
		digit_label[pick_digit] = 1 

		if pick_digit == 10:
			blank_image = np.ones((28,28,3), np.uint8)
			blank_image = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)
			random_int2=np.random.randint(0,4, size=1)
			for i in range(random_int2[0]):
				random_int=np.random.randint(1,29, size=2)
				random_int1=np.random.randint(0,6, size=1)
				cv2.circle(blank_image,(random_int[0],random_int[1]), random_int1[0], (255,255,255), -1)
			buf = cv2.bitwise_not(blank_image)
			#cv2.imshow('',buf)
			#cv2.waitKey(0)

		else:
			img_FD = cv2.imread('./Flaming_Digits/%d.jpg'%(pick_digit), cv2.IMREAD_COLOR)
			#print (digit_label)
			img_FD = img_FD[y:y+150,x:x+150]
			#cv2.imshow('',img_FD)
			#cv2.waitKey(0)
			img_FD = cv2.cvtColor(img_FD, cv2.COLOR_BGR2GRAY)
			_,buf = cv2.threshold(img_FD,200,255,cv2.THRESH_TOZERO+cv2.THRESH_OTSU)
			edged = cv2.Canny(buf, 255, 255)
			_, contours, hierarchy = cv2.findContours(edged.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
			cv2.drawContours(buf, contours, -1, 255,-1)
			buf = cv2.resize(buf,(30,32))
			uniform_random = np.random.uniform(0.7,1.0,2)
			buf = cv2.resize(buf,None,fx=uniform_random[0], fy=uniform_random[1])
			#print uniform_random
			uniform_random1 = np.random.uniform(-1.0,1.0,2)
			#uniform_random[0] *
			M = np.float32([[1,0,int(uniform_random1[0]*7)],[0,1,int(uniform_random1[1]*7)]])
			buf = cv2.warpAffine(buf,M,(30,32))
			kernel = np.ones((2,2),np.uint8)
			buf = cv2.bitwise_not(buf)
			random_int=np.random.randint(0,2, size=2)
			random_int1=np.random.randint(2, size=1)
			for i in range(random_int1[0]):
				buf=cv2.erode(buf,kernel,iterations = random_int[0])
				buf=cv2.dilate(buf,kernel,iterations = random_int[1])
			#cv2.imshow('',buf)
			#cv2.waitKey(0)

		buf = cv2.resize(buf,(28,28))
		#cv2.imshow('',buf)
		#cv2.waitKey(0)
		buf=np.array(buf)
		buf = 255 - buf
		buf = np.float32(buf) / 255.
		buf = buf.reshape([-1])
		#print buf
		#print buf.shape
		img.append(buf)
		y_label.append(digit_label)
	return img , y_label

def build_model(img_input):
	# can change whatever activation function
	with tf.variable_scope('FD_detection'):
		mod = M.Model(img_input,[None,28*28])
		mod.reshape([-1,28,28,1])
		mod.convLayer(5,16,activation=M.PARAM_LRELU)
		mod.maxpoolLayer(2)
		mod.convLayer(5,16,activation=M.PARAM_LRELU)
		mod.maxpoolLayer(2)
		mod.convLayer(5,16,activation=M.PARAM_LRELU)
		mod.maxpoolLayer(2)
		mod.flatten()
		mod.dropout(0.9)
		mod.fcLayer(50,activation=M.PARAM_LRELU)
		mod.dropout(0.8)
		mod.fcLayer(11)
	return mod.get_current_layer()

def build_graph():
	img_holder = tf.placeholder(tf.float32,[None,28*28])
	lab_holder = tf.placeholder(tf.float32,[None,11])
	last_layer = build_model(img_holder)
	loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=lab_holder,logits=last_layer))
	accuracy = M.accuracy(last_layer,tf.argmax(lab_holder,1))
	train_step = tf.train.AdamOptimizer(0.0001).minimize(loss)
	return img_holder,lab_holder,loss,train_step,accuracy,last_layer

img_holder,lab_holder,loss,train_step,accuracy,last_layer = build_graph()

with tf.Session() as sess:
	saver = tf.train.Saver()
	M.loadSess('./model/',sess,init=True)
	for i in range(100000):
		x_train, y_train = PickSevenSegment(BSIZE)
		_,acc,ls = sess.run([train_step,accuracy,loss],feed_dict={img_holder:x_train,lab_holder:y_train})
		if i%100==0:
			print('iter',i,'\t|acc:',acc,'\tloss:',ls)
		if i%5000==0 and i != 0:
			#acc = sess.run(accuracy,feed_dict={img_holder:mnist.test.images, lab_holder:mnist.test.labels})
			#print('Test accuracy:',acc)
			saver.save(sess,'./model_flaming/fd_%d.ckpt'%i)

