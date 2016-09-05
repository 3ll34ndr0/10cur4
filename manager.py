#!/usr/bin/python
# coding: latin-1
import json
import locale
# This should be tied to a configuration file:
locale.setlocale(locale.LC_ALL,'es_AR.utf8')
from dbapi import ActivityRegister,getUserRegister,humanActivityCreditsExpire

#####################################################################
# This code could be in a separate file and import the dictionary   #
# from that "module".                                               #
# Get a list of phones and database with hongaPor privileges        #
with open("hongaPors.txt", "r") as file:                            #
   hongaPors = file.readlines()                                     #
                                                                    #
hongaPorsOK = map(lambda pl: pl.rstrip('\n').split(','),hongaPors)  #
                                                                    #
databaseAccess = dict()                                             #
for [owner,database] in hongaPorsOK:                                #
   databaseAccess[owner] = database                                 #
#####################################################################
# Now whenever I want to access a database, I use the following     #
# dictionary:                                                       #
# databaseAccess[telephoneNumber]                                   #
#                                                                   #
#####################################################################
# TODO: Crear método que reserve turno y descuente crédito (sólo puede tener crédito negativo de -1?, creo
#       que no tiene que tener límites ó al menos diferenciar actividades con créditos o sin créditos). Y que envíe un pedido de confirmación al/la responsable de la actividad para aceptarla o no.

# TODO: Crear un método que cancele un turno, entre los reservados por la persona.
# TODO: Crear un método que cree nuevas actividades a partir de una lista con el siguiente formato:
#       lunes 10:00 12:00 14:30 18:00 21:15 23:00
# TODO: #1 Método que inicializa una cuenta, cuyo primer usuario (en adelante hongaPor) brinda un
#       email al cuál se le envia un código de confirmacion. Para qué sirve??Porque si perdés el celu,
#       te queda una oportunidadpara suspender los permisos administrativos de ese celu. En ese método,
#       se pregunta si el servicio para los/las clientes será prepago (basado en créditos) o no.
#
# TODO: #2: Método que permita agregar un administrador con acceso a una base de datos. Lo puede
#       hacer el/la usuario/a creada por el #1
# TODO: Método donde hongaPor puede pedir cualquier tipo de registro, para control de las tareas administrativas. Se recibe por un archivo de texto, por email, directamente por chat, según se elija

class ManageAppointments(ActivityRegister):
   """This class will give access to all method defined in the dbapi, and extend its functionality
      with lots of verifications before actually calling those methods... """
   def __init__(self, phoneNumber,activity):
     self.phoneNumber = phoneNumber
     self.activity    = activity
     self.initHour    = "0" # This initHour is a dummy value, just to start the object. Could I use it to store any useful data on it, like participants are the admins of that activity.
     self.database    = databaseAccess[self.phoneNumber]
     self.timeTuple   = None # (year,month,day,hour,minute)
     try:
        super(ManageAppointments, self).__init__(self.database,self.activity,self.initHour)
     except KeyError as e:
        print("Error: Your telephone's number has no access to this system")
   def makeAppointment(self,phoneNumber,activity,initHour):
      """ Add one phoneNumber to a given activity's initHour, if it exists and if the phone is
       in the database. """
      # Check if telephone exists in database (and also if at least has any
      # register in activities credits):
      try:
         phone, name, activityCreditsExpire, vCard = getUserRegister(self.database, phoneNumber)
         if activityCreditsExpire is not None:
            actCreditsDict = humanActivityCreditsExpire(activityCreditsExpire)
         print(phone, name, activityCreditsExpire, vCard)
         initHour = self.timeTuple
      # Done with checking if phone is in user's database.
      # Check if the activity initHour exists:
         reportAvailableAppointments(onDay=initHour)
      # Now make the friggin' appointment:
      #      ar = ActivityRegister(
      except TypeError as e:
         print("Error: That phone number does not belong to any registered user.")

#	def 

#   def asdfasdf:





