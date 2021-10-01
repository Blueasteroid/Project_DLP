# Video stimulus generator for TI DLP
# JH@KrappLab
# 2018-01-25 for DLP3000
# 2020-02-20 for DLP3010
#########################################
import cv2
import numpy as np
import time
import sys
#########################################

def gen_RotCav_stim(compress_flag = 1, output_fps = 360, debug_text = 1):
	h=720
	w=1280
	fps = output_fps 
	rps = 2 	### Unit: cycle per second 	### frequency: 2 cycle per second for intracellular stim (Krapp 1997)
	duration = 4.5 	### Unit: second 		### sequence: 0.5s null + 1.5s CW + 0.5s null + 1.5s CCW + 0.5s null

	fourcc=0
	if compress_flag == 1:
		fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
		# fourcc=cv2.VideoWriter_fourcc('X','V','I','D')
		# fourcc=cv2.VideoWriter_fourcc('D','I','B',' ')
	out = cv2.VideoWriter('stim.avi',fourcc, fps, (w,h))

	mask = np.zeros((h,w),np.uint8) 
	radius = 300
	for x in range(w):
		for y in range(h):
			if ((x-w/2)**2+(y-h/2)**2 <= radius**2):
				mask[y,x]=1

	deg_per_pattern = rps * 360 / fps  
	i=0  
	Total_Frame_Count = fps*duration 
	while(i < Total_Frame_Count): 
		frame = np.zeros((h,w,3),np.uint8) 

		if (i<0.5*fps or 2*fps<=i<2.5*fps or 4*fps<=i):
			pass

		elif (0.5*fps<=i<2*fps):	# CW
			### >>> background white disk <<< ###
			yy,xx=np.ogrid[0:h,0:w]
			mask_idx = (yy-h/2)**2+(xx-w/2)**2<=360**2
			frame[mask_idx,:]=0xFF
			### >>> rotating black disk <<< ###
			y=int(h/2-150*np.sin(i*np.pi/180*deg_per_pattern))
			x=int(w/2-150*np.cos(i*np.pi/180*deg_per_pattern))
			# yy,xx=np.ogrid[0:h,0:w]
			mask_idx = (yy-y)**2+(xx-x)**2<=120**2
			frame[mask_idx,:]=0x00


		elif (2.5*fps<=i<4*fps):	# CCW
			### >>> background white disk <<< ###
			yy,xx=np.ogrid[0:h,0:w]
			mask_idx = (yy-h/2)**2+(xx-w/2)**2<=360**2
			frame[mask_idx,:]=0xFF
			### >>> rotating black disk <<< ###
			y=int(h/2-150*np.sin(-i*np.pi/180*deg_per_pattern + np.pi))
			x=int(w/2-150*np.cos(-i*np.pi/180*deg_per_pattern + np.pi))
			# yy,xx=np.ogrid[0:h,0:w]
			mask_idx = (yy-y)**2+(xx-x)**2<=120**2
			frame[mask_idx,:]=0x00

		### corner sync dots ###
		if (np.sin(i*np.pi/180*deg_per_pattern)>0):
			yy,xx=np.ogrid[0:h,0:w]
			mask_idx = (yy-h/2-320)**2+(xx-w/2-320)**2<=40**2
			frame[mask_idx,:]=0xFF
			mask_idx = (yy-h/2+320)**2+(xx-w/2-320)**2<=40**2
			frame[mask_idx,:]=0xFF
			mask_idx = (yy-h/2-320)**2+(xx-w/2+320)**2<=40**2
			frame[mask_idx,:]=0xFF
			mask_idx = (yy-h/2+320)**2+(xx-w/2+320)**2<=40**2
			frame[mask_idx,:]=0xFF

		if debug_text == 1:
			cv2.putText(frame, #numpy array on which text is written
					"#"+str(i), #text
					(0,600), #position at which writing has to start
					cv2.FONT_HERSHEY_SIMPLEX, #font family
					3, #font size
					(255, 255, 255, 0), #font color
					3)

		out.write(frame)
		cv2.imshow('frame',frame)

		i+=1

		key = cv2.waitKey(1)
		if  key == ord('q') or key == 27:
			break

	out.release()
	cv2.destroyAllWindows()

#########################################

def encode_DLP_stim(compress_flag = 1, output_fps = 360):
	cap = cv2.VideoCapture('.\\stim.avi')
	if not cap.isOpened(): 
	    print( "could not open :",fn)
	    return

	input_fps = cap.get(cv2.CAP_PROP_FPS)
	w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # int
	h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # int
	Total_Frame_Count = cap.get(cv2.CAP_PROP_FRAME_COUNT)

	print('w, h =',w,h)
	print('total frame =',Total_Frame_Count)
	print('input_fps =',input_fps)

	fourcc=0
	if compress_flag == 1:
		fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
		# fourcc=cv2.VideoWriter_fourcc('X','V','I','D')
		# fourcc=cv2.VideoWriter_fourcc('D','I','B',' ')
	out = cv2.VideoWriter('encoded_stim.avi',fourcc, output_fps, (w,h))

	i = 0 
	while(i <= Total_Frame_Count-3): 

		DLP_frame = np.zeros((h,w,3), np.uint8)

		if (input_fps != 0) :
			cap.set(1,i)
			ret,frame1 = cap.read()
			cap.set(1,i+1)
			ret,frame2 = cap.read()
			cap.set(1,i+2)
			ret,frame3 = cap.read()

			### DLP3010 8-bit mode ### exposure = 2555 us, pre-dark = 171 us, post-dark = 31 us
			# DLP_frame[:,:,0] = frame1[:,:,0]	
			# DLP_frame[:,:,1] = frame2[:,:,0] 	
			# DLP_frame[:,:,2] = frame3[:,:,0]	

			### DLP3010 1-bit mode ### exposure = 1799 us, pre-dark = 500 us, post-dark = 500 us
			DLP_frame[:,:,0] = cv2.bitwise_or(cv2.bitwise_and(frame1[:,:,0], 0x80) ,DLP_frame[:,:,0])
			DLP_frame[:,:,0] = cv2.bitwise_or(cv2.bitwise_and(frame2[:,:,0], 0x40) ,DLP_frame[:,:,0])	
			DLP_frame[:,:,0] = cv2.bitwise_or(cv2.bitwise_and(frame3[:,:,0], 0x20) ,DLP_frame[:,:,0])

			DLP_frame[:,:,1] = cv2.bitwise_or(cv2.bitwise_and(frame1[:,:,0], 0x00) ,DLP_frame[:,:,1])
			DLP_frame[:,:,1] = cv2.bitwise_or(cv2.bitwise_and(frame2[:,:,0], 0x00) ,DLP_frame[:,:,1])	
			DLP_frame[:,:,1] = cv2.bitwise_or(cv2.bitwise_and(frame3[:,:,0], 0x00) ,DLP_frame[:,:,1])

			DLP_frame[:,:,2] = cv2.bitwise_or(cv2.bitwise_and(frame1[:,:,0], 0x00) ,DLP_frame[:,:,2])
			DLP_frame[:,:,2] = cv2.bitwise_or(cv2.bitwise_and(frame2[:,:,0], 0x00) ,DLP_frame[:,:,2])	
			DLP_frame[:,:,2] = cv2.bitwise_or(cv2.bitwise_and(frame3[:,:,0], 0x00) ,DLP_frame[:,:,2])

			# DLP_frame = cv2.cvtColor(DLP_frame, cv2.COLOR_BGR2RGB) # 

		else:
			print('input FPS error.')
			break

		i+=3
		print(i,end = '\r')		

		out.write(DLP_frame)
		cv2.imshow('frame',DLP_frame)

		key = cv2.waitKey(1)
		if  key == ord('q') or key == 27:
			break

	cap.release()
	out.release()
	cv2.destroyAllWindows()

##################################################
##################################################
##################################################

if __name__ == "__main__":

	# fps = 360 		# tested: 8-bit mode, generates unwanted 360Hz flickers
	fps = int(104.2 * 3) 	# test not finished yet
	print('[INFO] The output fps is:', fps)

	print('[INFO] Stage 1: Generating raw video stimulus...')
	gen_RotCav_stim(output_fps = fps)

	print('[INFO] Stage 2: Encoding raw video stimulus to DLP format...')
	encode_DLP_stim(output_fps = fps)

	print('[OVER] Programme end.')
