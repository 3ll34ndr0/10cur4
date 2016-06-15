class Horario(object):
	'''
	Objeto para guardar el horario de una actividad
	TODO: Quizas seria mas legible si fuese este formato:
	{'horarios': {{'initHour':'10'}: [{'endHour':'11'}, {'quota':'3'}, {'participants':set(['351519348', '35151938', '3515193486'])]}}, 'name': 'Bldy'}
	'''
	def __init__(self,activity,initHour,endHour,quota, participant=None):
		appointment 	= {}
		turnos	 	= {}
		appointment[initHour] = [endHour,quota,set([])]
		turnos[activity] = appointment
		self.name	= activity
		self.horarios = turnos[activity]
	def addParticipant(self,initHour,participant):
		'''
		Method to add a participant to an appointment		
		Params: initHour, participant
		participant: It is the participant's telephone number 
		'''
		try:
			totalP = str(len(self.horarios[initHour][2]))
			qota   = self.horarios[initHour][1]
			if totalP == qota:
			   message = 'Message: Turno completo, no se puede inscribir'
			else:
			   self.horarios[initHour][2].add(participant)
			   message  = "Message: {0} has been added to {1} at {2}\n".format(participant,self.name, initHour)
			   message += "AdminMessage: {3} participants in {1} at {2}".format(participant,self.name,initHour,totalP)
		except KeyError as e:
			message = "Message: There is no appointment for {} at {}".format(self.name, initHour)
		finally:
			return message 
#		print("%s participants: %s" % (qota,self.horarios[initHour][2]))
#		print("Quota %s" % qota )


	def addAppointment(self,initHour,endHour,quota, participant=None):
		'''
		Params: initHour, endHour,quota
		'''
		if participant == None: 
			participantSet = set([])
		else:
			participantSet = set(participant)
		self.horarios[initHour] = [endHour,quota,participantSet]
	def removeParticipant(self,initHour,participant):
		'''
		Method to remove a participant from a given appointment
		Params: initHour, participant 
		participant: It is the participant's telephone number 
		'''
		try:
			self.horarios[initHour][2].remove(participant)
			message = "Message: {} has been removed from {} at {}".format(participant,self.name, initHour)
		except KeyError as e:
			message = "Message: {} has no appointment to {} at {}".format(participant,self.name, initHour)
		except Exception as e: # Is this catch all error needed?
			raise e
		finally:
			return message

#claseJorge = Horario('Bldy','10','11','3')
##claseJorge.addParticipant('10','3515193486')
#claseJorge.removeParticipant('10','3515193486')
#claseJorge.removeParticipant('10','3515193486')
#
#claseJorge.addParticipant('10','351519348')
#claseJorge.addParticipant('10','35151938')
#claseJorge.__dict__
#claseJorge.addParticipant('10','3515193')

