class Horario(object):
	'''
	Objeto para guardar el horario de una actividad
	TODO: Quizas seria mas legible si fuese este formato:
	{'horarios': {{'initHour':'10'}: [{'endHour':'11'}, {'quota':'3'}, {'participants':set(['351519348', '35151938', '3515204597'])]}}, 'name': 'Bldy'}
	Quota is 1 as default
	'''
	def __init__(self,activity,initHour,endHour,quota='1', participant=None):
		appointment 	= {}
		turnos	 	= {}
		if participant is not None:
			if type(participant) is str: # If it is only one number, create a list
				participant = [participant]
			if len(participant) > quota:
				return "Message: Quota is smaller than participants' number"
			else:
				participantSet = set(participant)
		else: 
			participantSet = set([])
		appointment[initHour] = [endHour,quota,participantSet]
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
			if type(participant) is str:
				participant = [participant]
			newP   = len(participant)
			if totalP == qota:
			   message  = 'Message: Turno completo, no se puede inscribir'
			elif (newP + int(totalP)) > int(qota):
		           message  = "Message: No puede reservar {} lugare/s".format(str(newP))
			   message += ", la disponibilidad es de {}".format((str(int(qota)-int(totalP))))
			else:
			   self.horarios[initHour][2].update(participant)
			   message  = "Message: {0} has been added to"
			   message += " {1} at {2}\n"
			   message += "AdminMessage: {3} participants"
			   message += "in {4} at {5}"
			   message.format(participant,self.name,initHour,participant,self.name,initHour)
		except KeyError as e:
			message = "Message: There is no appointment for {} at {}".format(self.name, initHour)
		finally:
			message = ''
			return message 


	def addAppointment(self,initHour,endHour,quota='1', participant=None):
		'''
		Params: initHour, endHour,quota
		'''
		if participant == None: 
			participantSet = set([])
		elif type(participant) is str: # Only one element given
			participantSet = set([participant])
		else:
			participantSet = set(participant)
		self.horarios[initHour] = [endHour,quota,participantSet]
	def removeParticipant(self,initHour,participant):
		'''
		Method to remove a participant from a given appointment
		Params: initHour, participant 
		participant: It is the participant's telephone number,
		it can be a set, a list, or a string

		'''
		try:
			if type(participant) is str: # It is only one number
				print("tb es str")
				participant = set([participant])
			elif type(participant) is list:
				participant = set(participant)
			newPart = self.horarios[initHour][2] - participant # new participants' set
			self.horarios[initHour][2] = newPart # update set
			message = "Message: {} has been removed at {}".format(participant, initHour)
			print(message)
		except KeyError as e:
			message = "Message: {} has no appointment to {} at {}".format(participant,self.name, initHour)
		except Exception as e: # Is this catch all error needed?
			message = "Message: Exception for catch all error"
			raise e
		finally:
			return message 

