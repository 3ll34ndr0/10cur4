#!/usr/bin/python
# coding: latin-1
import unittest
import random
import json
from time import time,mktime,localtime
from dbapi import ActivityRegister, createActivityRegister,createUserRegisterDB,getUserRegister,formatDate
import locale
locale.setlocale(locale.LC_ALL,'es_AR.utf8')


database = 'test.db'
activity = 'Juanchos Gym'

################################################################
################################################################
import datetime
from datetime import timedelta
from time import time,mktime
import locale
locale.setlocale(locale.LC_ALL,'es_AR.utf8')
################################################################
horariosDisponibles = [timedelta(hours=hour) for hour in range(10,23,2)]
today = datetime.date.today()
todayAtZeroAM = datetime.datetime.combine(today,datetime.time(0,0))
daysOfThisWeek = [todayAtZeroAM+timedelta(days=i) for i in range(0,6)]
a = [[dia+hora for hora in horariosDisponibles] for dia in daysOfThisWeek]
piletaHorarios = list()
for i in a:
   for j in i:
      piletaHorarios.append(mktime(j.timetuple()))

################################################################

daysOfThisWeekHuman = map(lambda d: d.strftime("%A %d %B"),daysOfThisWeek)
initHour = random.sample(piletaHorarios,1).pop()
#initHour = str(random.randint(0,23))
#participantes = list(ActivityRegister(database, activity,initHour).participants)
# This numbers has to be valid user number, or it will fail in some stage of the test
#ActivityRegister(database, activity,'13',quota='3').update(quota='3')
with open("phoneNumbers.txt", "r") as file:
	   participants = file.readlines()

participantsOK = map(lambda pl: pl.rstrip('\n'),participants)

#print participantes
#createAppointmentDB(database)
class ActivityRegisterTest(unittest.TestCase):
    def setUp(self):
        self.activity     = activity
	self.initHour     = str(initHour)
	self.endHour      = None
	self.quota        = "1" # if ever change this, should use the update(quota='newvalue')
	self.participants = map(unicode,random.sample(participantsOK, random.randint(0,int(self.quota))))
	self.description  = "una cosa nomas te digo..."
	self.vCalendar    = "algun dia sera usado"
	self.database     = database
    def testParticipants(self):
	# Create an object and add participants
        timeTuple                 = localtime(float(self.initHour))[0:5]
        horaHumana,fechaHumana,z  = formatDate(timeTuple)
	print("Going to create an entry for {} at {} on {}".format(self.activity,horaHumana,fechaHumana))
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
    def testReport(self):
       ar = ActivityRegister(database, self.activity, self.initHour,self.endHour,self.quota)
       print(ar.rawReport())

### 
#Get a list with fake's names from a file. 
#nombres = list()
#with open("fake_names.txt","r") as file:
#   nombres = file.readlines()
####

#nombresOK  = map(lambda nl: nl.rstrip(' \n'),nombres)


#class UserRegisterDBTest(unittest.TestCase):
#   def setUp(self):
#      self.database = database
#      self.name     = map(unicode,random.sample(nombresOK,1)).pop()
#      self.activity = activity 
#      self.credit   = unicode(random.sample(range(8,32),1).pop()) 
#      self.phone    = map(unicode, random.sample(participants,1)).pop()
#      self.vCard    = createVcard(self.name,self.phone)
#      self.expDate  = str(time() + 2628000) # SEE: "def createUserRegisterDB" 
#   def testCreateUserReg(self):
#      createUserRegisterDB(self.database,
#		           self.phone,
#			   self.name,
#			   self.activity,
#			   self.credit,
#			   self.vCard)
#      userData  = getUserRegister(self.database,self.phone)
#      dictioAct = {self.activity:'@'.join((self.credit,self.expDate))}
#      credAtExp = json.dumps(dictioAct)
##      expected  = (self.phone, self.name,credAtExp,self.vCard)
#      self.assertEqual(userData,expected)

if __name__ == '__main__':
	    unittest.main()
