#!/usr/bin/python
# coding: latin-1
import unittest
import random
import json
from time import time
from dbapi import ActivityRegister, createActivityRegister,createUserRegisterDB,getUserRegister

database = 'test.db'
activity = 'Juanchos Gym'
#createAppointmentDB(database)
class ActivityRegisterTest(unittest.TestCase):
    def setUp(self):
#        self.activity     = "cosa loca"
        self.activity     = "cosa e locos"
	self.initHour     = str(random.randint(0,23)) 
#	self.initHour     = '12'
	self.endHour      = str(int(self.initHour)+1)+"hs"
	self.quota        = "270"
	self.participants = map(unicode,random.sample(range(4593515000000,4593515999999), random.randint(1,27)))
	self.description  = "una cosa nomas te digo..."
	self.vCalendar    = "algun dia sera usado"
	self.database     = database
    def testParticipants(self):
	# Create an object and add participants
	print("Going to create an entry for {} at  {}".format(self.activity,self.initHour))
	ar = ActivityRegister(self.database, self.activity, self.initHour,self.endHour,self.quota)
	#First delete all previous participants, if any
	delParticipants = ar.participants
	if delParticipants == []:
		print("El horario no tiene reservas")
	else:
		print("Borraré la siguiente lista: ")
		print(delParticipants)
	        ar.cancelAppointment(participants=delParticipants)
	print("Y ahora ...")
	print("agrego a la nueva gilada ...")
        ar.update(participants=self.participants)
	# First EQUIVALENCE TEST
	self.assertEqual(set(self.participants),set(ar.participants))
	#Create new object with data recently given
	br = ActivityRegister(self.database, self.activity, self.initHour)
	# New EQUIVALENCE TEST
	self.assertEqual(set(ar.participants),set(br.participants))
#    def testReport(self):
#       print("\n El horarido de initHour es: {} ".format(self.initHour))
#       ar = ActivityRegister(database, self.activity, self.initHour,self.endHour,self.quota)
#       print(ar.rawReport())

class UserRegisterDBTest(unittest.TestCase):
   def setUp(self):
      self.database = database
      [self.phone]  = map(unicode, random.sample(
		          range(4593515000000,4593515999999),1))
      self.name     = unicode('cualquier nombre')
      self.activity = activity 
      self.credit = unicode(random.sample(range(8,32),1).pop()) 
      self.vCard    = unicode('False vCard')
      self.expDate  = str(time() + 2628000) # SEE: "def createUserRegisterDB" 
   def testCreateUserReg(self):
      createUserRegisterDB(self.database,
		           self.phone,
			   self.name,
			   self.activity,
			   self.credit,
			   self.vCard)
      userData  = getUserRegister(self.database,self.phone)
      dictioAct = {self.activity:'@'.join((self.credit,self.expDate))}
      credAtExp = json.dumps(dictioAct)
      expected  = (self.phone, self.name,credAtExp,self.vCard)
      self.assertEqual(userData,expected)

if __name__ == '__main__':
	    unittest.main()
