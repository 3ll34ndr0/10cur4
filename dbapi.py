#!/usr/bin/python
# coding: latin-1
import sqlite3
import json
from horario import Horario
# Handle hours and date 
from datetime import datetime, timedelta
from pytz import timezone
import pytz
from time import time,localtime

class ActivityRegister(object):
   """
   This class is intended to create an object to handle the activity register in database.
   """
   def __init__(self,
		database,
		activity,
		initHour,
		endHour=None,
		quota='1'):
	self.database     = database
        self.activity     = activity
	self.initHour     = initHour
	self.endHour      = endHour
	self.quota        = quota
        # Try if the appointment exists:
	try:
            areg = getActivityRegister(database,activity) 
	    ar = json.loads(getActivityRegister(database,activity)[1])
	    ar['horarios'][initHour] # Esto es muy importante, se explica por la linea de arriba.
	except KeyError as e:
	    objetoHorario = self.loadReg()
	    print("Un horario a las {} no existe, sera creado...".format(initHour))
	    objetoHorario.addAppointment(initHour,endHour,quota=quota)
	    try:
		# Because we added one new initHour, need to write it to database
	        self.writeDatabase(objetoHorario)
                # Update this object with database values
                self.__init__(self.database,self.activity,self.initHour)
                areg = getActivityRegister(database,activity) 
	        ar = json.loads(getActivityRegister(database,activity)[1])
	    except Exception as e:
		#"Failed trying to write to database"
		raise e
            areg = getActivityRegister(database,activity) 
            ar = json.loads(getActivityRegister(database,activity)[1])
	except TypeError as e:
	    print("La actividad {} no existe, sera creada...".format(activity))
	    createActivityRegister(database,activity,initHour,endHour,quota=quota)
            areg = getActivityRegister(database,activity) 
	    ar = json.loads(getActivityRegister(database,activity)[1])

	self.endHour      = ar['horarios'][initHour][0]
	self.quota        = ar['horarios'][initHour][1]
	self.participants = ar['horarios'][initHour][2]
	self.description  = areg[3]
	self.vCalendar    = areg[4]
	self.name         = areg[0] 
	self.defaultQuota = areg[2]
   def rawReport(self):
       """Outputs all users and its data 
       in a given activity at an initHour
       """
       people  = getParticipantsName(self.participants)
       #rawData = '{},{}'.format(self.activity,self.initHour),people
       rawData = '{},{}'.format(self.activity,self.initHour,self.participants)
       return rawData

   def update(self,
		endHour=None,
		quota='1',
		participants=None,
		description=None,
		vCalendar=None):
	"""Method to update any value from activity.
	Optional params:
	endHour,
	quota,
	participants (If phone numbers are given with the '-' sign, they will be
	deleted),
	description,
	vCalendar.
	"""
        # Update endHour and quota:
        if endHour == None:
	    endHour = self.endHour
	else:
	    self.endHour = endHour
        if quota   == '1':
	    quota = self.quota
	else :
	    self.quota = quota
        #
	objetoHorario = self.loadReg()
	# Modify temporarly Horario object with updated values, except for participants
	objetoHorario.addAppointment(self.initHour,endHour,quota,self.participants)
        if participants is not None:
	    delParticipants = []
	    addParticipants = []
	    if type(participants) is str:
                if participants.startswith('-'):
		     # create remove
                     delParticipants = participants.strip('-')
		elif participants.isdigit():
		     # create Add
		     addParticipants = participants
		else:
		     print("Participant is not a valid telephon number")
	    elif type(participants) is list:
                # Create a list with numbers to remove from participants:
		delParticipants = set([item.strip('-') for item in participants if item.startswith('-')])
	        # Create a list with numbers to add to participants:
	        addParticipants = set([item for item in participants if item.isdigit()])
	    # Remove participants
	    objetoHorario.removeParticipant(self.initHour,delParticipants)
	    # Add participants
            objetoHorario.addParticipant(self.initHour,addParticipants)
        # Now that everything was done this auxiliary Horario object, dump it to DDDBB:
        # Write to database
        self.writeDatabase(objetoHorario,description=description,vCalendar=vCalendar)
        # Update this object with database values
        self.__init__(self.database,self.activity,self.initHour)
#END of def update 
   def cancelAppointment(self, participants):
	"""Method to cancel the appointment of 'participants' from the current initHour"""
	# ACA SEGUIR el problema es que tengo que construir correctamente el objeto horario
	# sin perder información para poder borrar sòlo los participantes.
        objetoHorario = self.loadReg()
	# Remove participants
	objetoHorario.removeParticipant(self.initHour,participants)
	# Write to database
	self.writeDatabase(objetoHorario)
	# Update object with database values
	self.__init__(self.database,self.activity,self.initHour)

   def remove(self,
	       participants=None,
	       initHour=None
	       ):
	"""
	Method to remove participants, OR erase all information for a given initHour
	"""
	#Me parece un bug que initHour no checkee por None
	if (participants or initHour) is None:
	    return
        objetoHorario = Horario(self.name, self.initHour,self.endHour,self.quota,self.participants)
	if (participants is not None and initHour is not None):
	    return
            print("You can not use this method this way. You can delete either participants of the current initHour OR all information of a given initHour, not both.") 
	if participants is not None:
            objetoHorario.removeParticipant(self.initHour,participants)
	    # Write to database
	    self.writeDatabase(objetoHorario)
	    # Update object with database values
	    self.__init__(self.database,self.activity,self.initHour)
	if initHour is not None: # 'Erase' all information from activity at initHour
	     objetoHorario = Horario(self.name,self.initHour,'') 
	     description=''
	     vCalendar  =''
 	     # Write to database
	     self.writeDatabase(objetoHorario,description=description,vCalendar=vCalendar)
	     # Update object with database values
             self.__init__(self.database,self.activity,self.initHour)

   def writeDatabase(self,
	              objetoHorario,
		      description=None,
		      vCalendar=None):
	"""
	Useful method that only writes to DDBB
	"""
	horariosJSON  = json.dumps(objetoHorario, default=jdefault)
        try:	
    	    db = sqlite3.connect(self.database)
            cursor = db.cursor()
	    # Aca va un update only horario column.
            cursor.execute(
            '''UPDATE activityCalendar SET horarios = ? WHERE act = ? ''', (horariosJSON, self.activity))
            message = "Message: {}, ".format(horariosJSON)
            if description is not None:
	        cursor.execute(
	        '''UPDATE activityCalendar SET description = ? WHERE act = ? ''', (description, self.activity))
                message += "{}, ".format(description) 
		self.description = description
	    if vCalendar is not None:
	        cursor.execute(
	        '''UPDATE activityCalendar SET vCalendar = ? WHERE act = ? ''', (vCalendar, self.activity))
	        message += "{}, ".format(vCalendar) 
		self.vCalendar = vCalendar
	    message += "added to {}".format(self.activity) 
	    db.commit()
        except sqlite3.IntegrityError as e:
	    db.rollback()
	    raise e
        except sqlite3.OperationalError as e:
            db.rollback()
	    raise e
        finally:
	    locals()
    	    cursor.close()

   def loadReg(self):
      """Method that creates an Horario object from current activity and database data"""
      areg = getActivityRegister(self.database,self.activity) 
      horarios = json.loads(getActivityRegister(self.database,self.activity)[1])
      h = horarios['horarios']
      # Get all keys from 'horarios'
      keys = list(h.viewkeys())
      # Get the first key and create the object
      key = keys.pop()
      objetoHorario = Horario(self.activity, key, h[key][0], h[key][1], h[key][2])
      # Next, get all other keys and populate the object with data from ddbb
      while len(keys)>0:
         key = keys.pop()
         objetoHorario.addAppointment(key,h[key][0], h[key][1], h[key][2])
      return objetoHorario

   def getParticipantsName(self, participants):
      """Get all names and expire date from a given list of participants, from current database"""
      namesAndExpire = []
      for phone in participants:
         phone,name,expireDate,vCard = getUserRegister(self.database,phone) 	
	 namesAndExpire.append(name+','+expireDate.split('@'))
      
      return namesAndExpire


def createActivityRegister(
		database, 
		activity,
		initHour=None,
		endHour=None,
		quota='1', 
		description=None, 
		vCalendar=None):
    """
    Creo una entrada en la tabla con 'activity' y un horario.
    En cada tabla de actividad puedo agregar mas de un horario, por ejemplo: 
    lunes 18:30, lunes 20:30, martes 9:00, miercoles 13:00
    quota: Cantidad maxima de participantes permitida por horario (a las 13hs pueden
    8 pero a las 16hs pueden ser 20)
    TODO: Pasar los dias de la semana a minusculas siempre. Asegurar
    formato am/pm y/o formato 24hs para pm. Probablemente
    eso es en una capa superior. 
    """
    # Construyo el objeto tipo Horario:
    objetoHorario = Horario(activity,initHour,endHour,quota) 
    #print(objetoHorario.__dict__)
    horarios	  = json.dumps(objetoHorario, default=jdefault)
    try:	
        db = sqlite3.connect(database)
	cursor = db.cursor()
	cursor.execute(
	'''INSERT INTO activityCalendar(act, horarios, quota, description, vCalendar)
	VALUES(?,?,?,?,?)''', (activity, horarios, quota, description, vCalendar))
	print("DEBUG: Register %s, %s, %s, %s , %s added"% (activity, horarios, quota, description, vCalendar))
	db.commit()
    except sqlite3.IntegrityError as e:
	db.rollback()
	print("Existing record...")
	print(e) # Son necesarios los raise?, por las dudas lo saque para que no falle.
    except sqlite3.OperationalError as e:
	db.rollback()
	print("DEBUG: Diferenciar el tipo de error")
	raise e
    finally:
	cursor.close()


def modifyActivityRegister(
		database,
		activity,
		initHour,
		endHour=None,
		quota='1',
		participants=None,
		description=None,
		vCalendar=None):
    """
	Modifico algun valor de la tabla
	Horarios, cantidad maxima de participantes (quota)
	TODO: Chequear la integridad (formato) de los datos antes de guardar.
	horarios: "{'Dia':'(HoraComienzo,HoraFin,participants,quota),(HoraComienzo2,HoraFin2,participants,quota2),...)'}"
	horarios incluye la cantidad maxima de participantes  y lista de inscriptos (telefonos)
	Dia, HoraComienzo, horaFin, quota: Are UTF-8 strings
	participants is a set, including telephoneNumber's participants
	Dia: lunes|martes|... en minusculas.
	Hora: HH:MM
    """
    # Primero tengo que obtener de la base de datos, lo que haya
    activityRegister = getActivityRegister(database, activity)
    if activityRegister[0] == activity:
           # Luego transformalo en un objeto clase Horario
	   horarios = json.loads(activityRegister[1]) 
	   h = horarios['horarios']
	   for key in h.viewkeys():
	       objetoHorario = Horario(activity, key, h[key][0], h[key][1], h[key][2])
	       #print("dentro el for")
	       #print(h[key][2])
	       #print(objetoHorario.horarios[key][2])
	       # Recupero los valores para no pisarlos despues (solo el que modifica)
               if initHour == key:
	             participantsReg = objetoHorario.horarios[key][2]
		     #print("aca")
		     #print objetoHorario.horarios
		     #print(participantsReg)
		     if participants is not None:
			#print("New participants, but recovering old ones: {}".format(participantsReg))
#			#print(participantsReg)
		        participantsReg.update(participants)
		     if endHour     == None:
		        endHour = objetoHorario.horarios[key][0]
		     if quota       == '1':
		        quota = objetoHorario.horarios[key][1]
               else:
		     print("Appointment {key} is not going to be modified".format(key))
	       #print("{}, {}, {}, {}".format(key, h[key][0],h[key][1],participantsReg))
	   
           # Ya tengo el objeto, ahora puedo actualizarlo:
	   objetoHorario.addAppointment(initHour,endHour,quota, participantsReg)
           horariosJSON  = json.dumps(objetoHorario, default=jdefault)
	   #print(horariosJSON)
    else: 
	   return "Message: Not such activity defined"
    try:	
	db = sqlite3.connect(database)
        cursor = db.cursor()
	# Aca va un update only horario column.
	cursor.execute(
	'''UPDATE activityCalendar SET horarios = ? WHERE act = ? ''', (horariosJSON, activity))
	message = "Message: {}, ".format(horariosJSON)
	if description is not None:
	    cursor.execute(
	    '''UPDATE activityCalendar SET description = ? WHERE act = ? ''', (description, activity))
            message += "{}, ".format(description) 
	if vCalendar is not None:
	    cursor.execute(
	    '''UPDATE activityCalendar SET vCalendar = ? WHERE act = ? ''', (vCalendar, activity))
	    message += "{}, ".format(vCalendar) 
	message += "added to {}".format(activity) 
	db.commit()
    except sqlite3.IntegrityError as e:
	db.rollback()
	raise e
    except sqlite3.OperationalError as e:
	db.rollback()
	raise e
    finally:
	cursor.close()
    return message

def addActivityParticipant(
		database,
		activity,
		initHour,
		telephone):
    return modifyActivityParticipant(database,activity,initHour,telephone)



def getActivityRegister(database, activity):
	db = sqlite3.connect(database)
	actividad= (activity,) # Convert it to a tuple to use it in the 'execute'  
	cursor = db.cursor()
	lista = cursor.execute('SELECT * FROM activityCalendar WHERE act=?', actividad)
#	print lista
	otraLista = lista.fetchone()
#	print otraLista
	cursor.close()
	return otraLista # I could return data as: Name, activity (n credits expire on 'expireDate') 



def createAppointmentDB(database):
    """ 
        Database's name should be related to the client's market 
        Creates a database with: phone, name, activityCreditExpireDate, vCard 
	Phone number should include international code
    """
    try:
	db = sqlite3.connect(database)
	# Get a cursor object
	cursor = db.cursor()
	cursor.execute('''
		    CREATE TABLE IF NOT EXISTS cuentaUsuarios(phone TEXT PRIMARY KEY, 
                         	name TEXT, activityCreditExpire TEXT, vCard TEXT)
		       ''')
	# En principio solo uso act y horarios. En horarios guardo un json serializando un objeto clase Horarios
	cursor.execute('''
		    CREATE TABLE IF NOT EXISTS activityCalendar(act TEXT PRIMARY KEY, 
                    horarios TEXT, quota TEXT, description TEXT, vCalendar TEXT)
		       ''')
	db.commit()
    except Exception as e:
	# Roll back any change if something goes wrong
	db.rollback()
	raise e
    finally:
        # Close the connection database
	cursor.close()


def createUserRegisterDB(
		database=None,
		phone=None,
		name=None, 
		activity=None, 
		credit=None, 
		vCard=None, 
		expDate=None):
    """
	activity, credit and the expire date is stored
	in a Dictionary using activity as string key.
	Credit and ExpireDate will be stored as  should be as credit@expireDate.
	expireDate will be calculated on fly when credits are added.	
	Example: '{"act1" : "cred1@date1", "act2" : "cred2@date2", "act3" : ... }' 
	expDate should be in a defined format (for example: DD-MM-YYYY)
    """
    db = sqlite3.connect(database)
	# Get a cursor object
    cursor = db.cursor()
    if not activity == None: 
	    # Expire date
	    if expDate == None:
		    expDate = str(time() + 2628000)  #2628000 secs in a month 365.0/12
	    else:
		    print("TODO: Check if date is in the defined format DD-MM-YYYY, and convert it to epoch time")

            # Format activity, credits, expDate:
	    if credit == None: credit = 0 # We have activity but credit was not a given parameter, so make it zero

            creditAtDate = '@'.join((credit,expDate))
	    dictActivity = {activity: creditAtDate}
	    activityCreditExpire = json.dumps(dictActivity)
    else:
	    activityCreditExpire = activity # None
    try:	
        cursor.execute('''INSERT INTO cuentaUsuarios(phone, name, activityCreditExpire, vCard)
	VALUES(?,?,?,?)''', (phone, name, activityCreditExpire, vCard))
	print("Register %s, %s, %s, %s added"% (phone, name, activityCreditExpire, vCard))
	db.commit()
    except sqlite3.IntegrityError as e:
	db.rollback()
	raise e
    except sqlite3.OperationalError as e:
	db.rollback()
	#print("la garlopa")
	raise e
    finally:
	cursor.close()


def getUserRegister(database,phoneNumber):
   """Returns (phone, name, activityCreditsExpire,vCard) from database"""
   db = sqlite3.connect(database) #I should use try here
   telefono = (phoneNumber,)
   cursor = db.cursor()
   lista = cursor.execute('SELECT * FROM cuentaUsuarios WHERE phone=?', telefono)
   otraLista = lista.fetchone()
   cursor.close()
   return otraLista # Should I return data as: Name, activity (n credits expire on 'expireDate')? 


def modifyRegisterCredit(database, phoneNumber, activity, newCredits, name=None, vCard=None):
	"""
	This function can be used to add new fields or update existing ones.
	When adding new credits, it updates for 1 month the expire date.
	TODO: Take into account the type of each field (credits should be an int, ...)
	"""
	# First I get the whole register using that phone number
        (phone, name, activityCreditsExpire,vCard) = getUserRegister(database,phoneNumber) 	
	# Get activities' list
	if not activityCreditsExpire == None:
		print("tipo %s y valor: %s" % (type(activityCreditsExpire),activityCreditsExpire))
		activityDict= json.loads(activityCreditsExpire)
		(credits, oldExpireDate) = activityDict[activity].split('@')
	else:
	   	activityDict = {}
	   	credits = newCredits

	#######   Create new expire date if adding credits
	if int(newCredits) > 0: # When adding new credits, update expire date of credits
		expireDate = repr(time() + 2628000)  # Next month (30 days + 10 hs.) at this time in epoch format
	else:
		expireDate = oldExpireDate # Don't modify expire date because we are not adding new credits
	####### 

	# Get credits and activity's phoneNumber)
	# Find activity
	if activity in activityDict: # update only credits
	        credits = str( int(credits) + int(newCredits) ).encode('utf-8')

	activityDict[activity] = '@'.join((credits,expireDate))
	fechaHumana = strftime("%d %b %Y", localtime(float(expireDate)))
	print("En {0} tiene {1} creditos hasta el {2} inclusive".format(activity, credits, fechaHumana))
	# Now update register with new credit and activity data
	try:
		db = sqlite3.connect(database)
	 	cursor = db.cursor()
		cursor.execute('''UPDATE cuentaUsuarios SET activityCreditExpire = ? WHERE phone = ? ''',
			      (json.dumps(activityDict), phone))
		db.commit()
	except Exception as e:
		# Roll back any change if something goes wrong
		db.rollback()
		raise e
	finally: 
		cursor.close()


#db = sqlite3.connect('j1rn4s10')
# Get a cursor object
#cursor = db.cursor()

#cursor.execute('''SELECT phone, name, activityCreditExpire FROM cuentaUsuarios''')
#user1 = cursor.fetchone() #retrieve the first row
#print(user1[0]) #Print the first column retrieved(user's name)
#all_rows = cursor.fetchall()
#for row in all_rows:
#    # row[0] returns the first column in the query (name), row[1] returns email column.
#      print('{0} : {1}, {2}'.format(row[0], row[1], row[2]))

def jdefault(o):
	if isinstance(o, set):
		return list(o)
	return o.__dict__

# https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
def formatDate(hour,minute,day=None,month=None,year=None):
   """ Returns a tuple with the hour in HH:MM (AM|PM) format, 
   Locale’s appropriate date and time representation (e.g. Mon Sep 30 07:06:05 2013)
   and a datetime object if date is also given as parameter.
   """
   horaFecha     = None
   horaFecha_str = None
   if (day or month or year) is not None:
      horaFecha     = datetime.datetime.combine(
	                                   datetime.datetime(year,month,day),
					   datetime.time(hour,minute))
      horaFecha_str = horaFecha.strftime("%c") #Locale’s appropriate date and time representation.
   hora_str = datetime.time(hour,minute).strftime("%H:%M %p")
   return (hora_str,horaFecha_str,horaFecha) 
