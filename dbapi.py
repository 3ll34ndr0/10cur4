import sqlite3
import json
from horario import Horario
#           hourList = []
#	    daySchedule{}  = emptyDict[day.lower():hourList.append((initHour, endHour)]}
	    
def createActivityRegister(
		database, 
		activity,
		initHour=None,
		endHour=None,
		quota=None, 
		description=None, 
		vCalendar=None):
    '''
	Creo una entrada en la tabla con 'activity' y un horario.
	En cada tabla de actividad puedo agregar mas de un horario, por ejemplo: 
	lunes 18:30, lunes 20:30, martes 9:00, miercoles 13:00
	quota: Cantidad maxima de participantes permitida por horario (a las 13hs pueden
	       8 pero a las 16hs pueden ser 20)
	TODO: Pasar los dias de la semana a minusculas siempre. Asegurar
	      formato am/pm y/o formato 24hs para pm. Probablemente
	      eso es en una capa superior. 
    '''
    # Construyo el objeto tipo Horario:
    objetoHorario = Horario(activity,initHour,endHour,quota) 
    print(objetoHorario.__dict__)
    horarios	  = json.dumps(objetoHorario, default=jdefault)
    try:	
        db = sqlite3.connect(database)
	cursor = db.cursor()
	cursor.execute('''INSERT INTO activityCalendar(act, horarios, quota, description, vCalendar)
	VALUES(?,?,?,?,?)''', (activity, horarios, quota, description, vCalendar))
	print("DEBUG: Register %s, %s, %s, %s , %s added"% (activity, horarios, quota, description, vCalendar))
	db.commit()
    except sqlite3.IntegrityError as e:
	db.rollback()
	raise e  # Son necesarios los raise?
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
		quota=None,
		description=None,
		vCalendar=None):
    '''
	Modifico algun valor de la tabla
	Horarios, cantidad maxima de participantes (quota)
	TODO: Chequear la integridad (formato) de los datos antes de guardar.
	horarios: "{'Dia':'(HoraComienzo,HoraFin,participants,quota),(HoraComienzo2,HoraFin2,participants,quota2),...)'}"
	horarios incluye la cantidad maxima de participantes  y lista de inscriptos (telefonos)
	Dia, HoraComienzo, horaFin, quota: Are UTF-8 strings
	participants is a set, including telephoneNumber's participants
	Dia: lunes|martes|... en minusculas.
	Hora: HH:MM
    '''
    # Primero tengo que obtener de la tabla, lo que haya
    parametros = (initHour,endHour,quota,description,vCalendar)
    activityRegister = getActivityRegister(database, activity)
    # Luego transformalo en un objeto clase Horario
    if activityRegister[0] == activity:
	   horarios = json.loads(activityRegister[1]) 
	   h = horarios['horarios']
	   for key in h.viewkeys():
		       objetoHorario = Horario(activity, key, h[key][0], h[key][1], h[key][2])
		       # Recupero los valores para no pisarlos despues (solo el que modifica)
		       if initHour == key:
		 	     participants = objetoHorario.horarios[key][2]
			     print objetoHorario.horarios[key][2]
		             if endHour == None:
			        endHour = objetoHorario.horarios[key][0]
		             if quota == None:
			        quota = objetoHorario.horarios[key][1]
		       print("{}, {}, {}".format(key, h[key][0],h[key][1]))
           # Ya tengo el objeto, ahora puedo actualizarlo:
	   objetoHorario.addAppointment(initHour,endHour,quota, participants)
           horariosJSON  = json.dumps(objetoHorario, default=jdefault)
	   print(horariosJSON)
    else: 
	   return "Message: Not such activity defined"
    try:	
	db = sqlite3.connect(database)
        cursor = db.cursor()
	# Aca va un update.
	cursor.execute('''UPDATE activityCalendar SET horarios = ? WHERE act = ? ''', (horariosJSON, activity))
	message = "Message: {}, {}, {}, {} added to {}".format(horarios, quota, description, vCalendar, activity ) 
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
    # First get the data from DB and load it in the Horario object
    message = ''
    activityRegister = getActivityRegister(database, activity)
#    print(activityRegister)
    # Luego transformalo en un objeto clase Horario
    if activityRegister[0] == activity:
	   horarios = json.loads(activityRegister[1]) 
	   h = horarios['horarios']
	   for key in h.viewkeys():
	       print(key)
	       objetoHorario = Horario(activity, key, h[key][0], h[key][1], h[key][2])

               print(objetoHorario.__dict__)
           # Ya tengo el objeto, ahora puedo actualizarlo:
    message += objetoHorario.addParticipant(initHour, telephone)
    horariosJSON  = json.dumps(objetoHorario, default=jdefault)
#    print(horariosJSON)
#    else: 
	  # return "Message: Not such activity defined"
    try:	
	db = sqlite3.connect(database)
        cursor = db.cursor()
	# Aca va un update.
	cursor.execute('''UPDATE activityCalendar SET horarios = ? WHERE act = ? ''',
    (horariosJSON, activity))
	message = "Message: {} added to {}".format(horarios, activity ) 
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
    ''' 
        Database's name should be related to the client's market 
        Creates a database with: phone, name, activityCreditExpireDate, vCard 
	Phone number should include international code
    '''
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


def createUserRegister(
		database=None,
		phone=None,
		name=None, 
		activity=None, 
		credit=None, 
		vCard=None, 
		expDate=None):
    '''
	activity, credit and the expire date is stored
	in a Dictionary using activity as string key.
	Credit and ExpireDate will be stored as  should be as credit@expireDate.
	expireDate will be calculated on fly when credits are added.	
	Example: '{"act1" : "cred1@date1", "act2" : "cred2@date2", "act3" : ... }' 
	expDate should be in a defined format (for example: DD-MM-YYYY)
    '''
    db = sqlite3.connect(database)
	# Get a cursor object
    cursor = db.cursor()
    if not activity == None: 
	    # Expire date
	    if expDate == None:
		    expireDate = time() + 2628000  #2628000 secs in a month 365.0/12
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
	print("la garlopa")
	raise e
    finally:
	cursor.close()


def getUserRegister(database,phoneNumber):
	db = sqlite3.connect(database)
	telefono = (phoneNumber,)
	cursor = db.cursor()
	lista = cursor.execute('SELECT * FROM cuentaUsuarios WHERE phone=?', telefono)
	otraLista = lista.fetchone()
	cursor.close()
	return otraLista # I could return data as: Name, activity (n credits expire on 'expireDate') 


def modifyRegisterCredit(database, phoneNumber, activity, newCredits, name=None, vCard=None):
	'''
	This function can be used to add new fields or update existing ones.
	When adding new credits, it updates for 1 month the expire date.
	TODO: Take into account the type of each field (credits should be an int, ...)
	'''
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

   
#json.dumps(horarioObject,default=jdefault)
#json.loads(json.dumps())

