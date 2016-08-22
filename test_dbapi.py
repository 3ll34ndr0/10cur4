#!/usr/bin/python
# coding: latin-1
import unittest
import random
from dbapi import ActivityRegister, createActivityRegister
database = 'test.db'
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

	   # Create new object with data recently given
#	   br = ActivityRegister(self.database, self.activity, self.initHour)
#	   self.assertEqual(set(self.participants),set(br.participants))
#	except TypeError as e:
#	   print("Opaaa! Activity {} has no record on database, creating it...".format(self.activity))
#           createActivityRegister(database,
#                                 self.activity,
#	                         initHour=self.initHour,
#	                         endHour=self.initHour,
#	                         quota=self.quota,
#	                         description=self.description,
#	                         vCalendar=self.vCalendar)
    def testReport(self):
       print("\n El horarido de initHour es: {} ".format(self.initHour))
       ar = ActivityRegister(database, self.activity, self.initHour,self.endHour,self.quota)
       print(ar.rawReport())

if __name__ == '__main__':
	    unittest.main()
