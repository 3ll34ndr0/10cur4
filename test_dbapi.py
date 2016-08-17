import unittest
import random
from dbapi import ActivityRegister, createActivityRegister
database = 'test.db'
#createAppointmentDB(database)
class ActivityRegisterTest(unittest.TestCase):
    def setUp(self):
        self.activity     = "motor home"
	self.initHour     = str(random.randint(0,23)) 
	self.endHour      = str(int(self.initHour)+1)+"hs"
	self.quota        = "27"
	self.participants = map(unicode,range(5000000,5000010))
	self.description  = "una cosa nomas te digo..."
	self.vCalendar    = "algun dia sera usado"
	self.database     = database


    def testParticipants(self):
	# Create an object and add participants
	print("Going to create an entry for {}".format(self.initHour))
	try:
	   ar = ActivityRegister(database, self.activity, self.initHour,self.endHour,self.quota)
           participants = ar.update(participants=self.participants)
	   # Create new object with data recently given
	   br = ActivityRegister(database, self.activity, self.initHour,self.endHour,self.quota)
	   self.assertEqual(set(self.participants),set(br.participants))
	except TypeError as e:
	   print("Opaaa! Activity {} has no record on database, creating it...".format(self.activity))
           createActivityRegister(database,
                                 self.activity,
	                         initHour=self.initHour,
	                         endHour=self.initHour,
	                         quota=self.quota,
	                         description=self.description,
	                         vCalendar=self.vCalendar)


    def test_createActivtyRegister(self):
	""" Just create the activity with all data
	Creo que esto no es necesario ya que 
	si no existe la actividad, se crea
	capturando la excepción en testParticipants
        createActivityRegister(database,
	self.activity,
	initHour=self.initHour,
	endHour=self.initHour,
	quota=self.quota,
	description=self.description,
	vCalendar=self.vCalendar)
	"""
	print(".")



if __name__ == '__main__':
	    unittest.main()
