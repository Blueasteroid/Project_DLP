#!/usr/bin/env python

###########################
# Author: JH@KrappLab
# 2018-01-17
###########################

import socket
import time
# import imageio
import sys,os




class DLP_LightCrafter:
	def __init__(self, IP='192.168.1.100'):
		self.TCP_IP = IP
		self.TCP_PORT = 0x5555
		self.BUFFER_SIZE = 1024
		self.check_IP(self.TCP_IP)

		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((self.TCP_IP, self.TCP_PORT))


	def check_IP(self, IP):
		if os.system("ping -n 1 -w 1000 "+IP+" > nul ") == 1 :
			print("WARN: Connection to IP "+IP+" is broken. please check...")
			exit()
		else:
			print("INFO: Connection to IP "+IP+" is OK.")	

	def disconnect_DLP(self):
		self.s.close()

	def send(self, msg, echoflag=0):
		checksum = 0
		for i in range(len(msg)):
			checksum += int(msg[i])
		checksum=checksum % 0x100

		tcp_msg = msg + bytes([checksum])

		if echoflag == 1:
			print("SEND:",tcp_msg[0:9],"...",tcp_msg[-5:])

		# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# s.connect((self.TCP_IP, self.TCP_PORT))
		self.s.send(tcp_msg)	
		data = self.s.recv(self.BUFFER_SIZE)
		# s.close()

		if echoflag == 1:
			print ("ECHO:", data)
			print ("DONE!")


	def setDisplayMode(self, load=2):
		HEAD = b'\x02'
		COMM = b'\x01'+b'\x01'
		FLAG = b'\x00'
		SIZE = b'\x01'+b'\x00'
		LOAD = bytes([load])
		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)

	def setTestPattern(self, load=1):
		HEAD = b'\x02'
		COMM = b'\x01'+b'\x03'
		FLAG = b'\x00'
		SIZE = b'\x01'+b'\x00'
		LOAD = bytes([load])
		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)

	def setVideoInput(self):
		ResolutionX=608
		ResolutionY=684
		LeftCrop=0
		TopCrop=0
		RightCrop=608
		BottomCrop=684

		HEAD = b'\x02'
		COMM = b'\x02'+b'\x00'
		FLAG = b'\x00'
		SIZE = b'\x0c'+b'\x00'
		LOAD = bytes([ResolutionX%256,ResolutionX//256,
						ResolutionY%256,ResolutionY//256,
						LeftCrop%256,LeftCrop//256,
						TopCrop%256,TopCrop//256,
						RightCrop%256,RightCrop//256,
						BottomCrop%256,BottomCrop//256,
						])

		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)

	def getVersionString(self, load=0x10):
		HEAD = b'\x04'
		COMM = b'\x01'+b'\x00'
		FLAG = b'\x00'
		SIZE = b'\x01'+b'\x00'
		LOAD = bytes([load])
		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)




	def loadStaticImage(self,img="demo.bmp"):
		print("INFO: Uploading file -",img)
		with open(img, "rb") as imageFile:
			f = imageFile.read()
			b = bytearray(f)

		imlen = len(b)
		# print ("TEST: image length =", imlen)
		index = 0		
		### need to cut the file into pieces ###
		### to do ... ###
		HEAD = b'\x02'
		COMM = b'\x01'+b'\x05'
		FLAG = b'\x01'
		# SIZE = b'\xff'+b'\xff'
		LOAD = b[0:0xffff]
		SIZE = bytes([len(LOAD)%256,len(LOAD)//256])
		# print ("TEST: load length =", len(LOAD))
		# print ("TEST:",len(b[0:0xffff]))
		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)
		index += 0xffff
		# time.sleep(0.01)

		while ((imlen-index)>0xffff):
			# HEAD = b'\x02'
			# COMM = b'\x01'+b'\x05'
			FLAG = b'\x02'
			# SIZE = b'\xff'+b'\xff'
			LOAD = b[index:index+0xffff]
			SIZE = bytes([len(LOAD)%256,len(LOAD)//256])
			# print ("TEST: load length =", len(LOAD))
			MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
			self.send(MESSAGE)
			index += 0xffff
			# time.sleep(0.01)

		# HEAD = b'\x02'
		# COMM = b'\x01'+b'\x05'
		FLAG = b'\x03'
		# SIZE = bytes([(imlen-index)%256,(imlen-index)//256])
		LOAD = b[index:imlen]
		SIZE = bytes([len(LOAD)%256,len(LOAD)//256])
		# print ("TEST: load length =", len(LOAD))
		# print ("TEST:",len(b[index:imlen]))
		MESSAGE = HEAD+COMM+FLAG+SIZE+LOAD
		self.send(MESSAGE)
		# index += 0x10000



if __name__ == "__main__":

	d = DLP_LightCrafter("192.168.1.100")

	# d.getVersionString()
	# d.setVideoInput()

	# d.setDisplayMode(1)
	# for i in range(14):
	# 	d.setTestPattern(i)
	# 	time.sleep(1)

	# d.setDisplayMode(2)
	# time.sleep(2)

	d.setDisplayMode(0)
	d.loadStaticImage("demo.bmp")
	d.loadStaticImage("demo1.bmp")
	d.loadStaticImage("demo.bmp")
	d.loadStaticImage("demo1.bmp")
	


	d.disconnect_DLP()
