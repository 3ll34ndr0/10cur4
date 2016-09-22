#!/usr/bin/python
# coding: latin-1
import json
import locale
from dbapi import formatDate, createUserRegisterDB
import time
# This should be tied to a configuration file:
locale.setlocale(locale.LC_ALL,'es_AR.utf8')
#####################################################################
#                                                                   #
#   dbapi module where all the data access methods are provided     #
#                                                                   #
from dbapi import ActivityRegister, getUserRegister, humanActivityCreditsExpire
#####################################################################

#####################################################################
# This code could be in a separate file and import the dictionary   #
# from that "module".                                               #
# Get a list of phones and database with hongaPor privileges        #
with open("/home/lean/arena/10cur4/hongaPors.txt", "r") as file:                            #
   hongaPors = file.readlines()                                     #
                                                                    #
hongaPors = map(lambda pl: pl.rstrip('\n').split(','),hongaPors)    #
                                                                    #
databaseAccess = dict()                                             #
for [owner,database,activity] in hongaPors:                         #
   databaseAccess[owner] = database,activity                        #
#####################################################################
# Now whenever I want to access a database, I use the following     #
# dictionary:                                                       #
# databaseName,defaultActivity = databaseAccess[telephoneNumber]    #
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
   def __init__(self, phoneNumber,activity=None):
     self.phoneNumber = phoneNumber
     self.initHour    = "0" # This initHour is a dummy value, just to start the object. Could I use it to store any useful data on it, like participants are the admins of that activity.
     self.timeTuple = None # (year,month,day,hour,minute)
     try:
        if activity is None:
            self.database,self.activity = databaseAccess[self.phoneNumber]
        else:
            self.database,_ = databaseAccess[self.phoneNumber]
            self.activity   = activity
        super(ManageAppointments, self).__init__(self.database,self.activity,self.initHour)
        self.accountType     = "manager"
        self.defaultActivity = activity
     except KeyError as e:
        print("Error: Your telephone's number has no access to this system")
        print("or there is no activity named as {}".format(activity))
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
         self.timeTuple = initHour
      except TypeError as e:
         print("Error: That phone number does not belong to any registered user.")
         raise e
      # Done with checking if phone is in user's database.
      # Check if the activity initHour exists:
      initHourEpoch= formatDate(initHour.timetuple()[0:5])[2]
      aaps = map(float,
                 self.reportAvailableAppointments(onDay=initHour.replace(hour   = 0,
                                                                         minute = 0)))
      print(initHour,map(lambda x: time.localtime(x),aaps))
      if initHourEpoch in aaps:
             print("Bingoooo!")
             print("available appointment at {}".format(initHour))
      else:
             print("Message: No available appointment at {}".format(initHour))
      # Now make the friggin' appointment:
      #      ar = ActivityRegister(
   def createUserRegisterFromVCard(self,vCard,activity=None,credit=None,expDate=None):
          import vobject
#   if (activity or credit) is not None: return "You must give both values: activity and credits. Or you can give nither of them"
          vcObj = vobject.readOne(vCard)
          name  = vcObj.contents['fn'][0].value
          phonedata = vcObj.contents['tel'][0].value
          phone = phonedata.lstrip('+').replace(' ','').replace('-','') #Not very elegant, but ...
          createUserRegisterDB(self.database,
		        phone,
			name,
			activity,
			credit,
			vCard,
			expDate)



class VistaMinable(ActivityRegister):
    """Esta clase será utilizada para crear una vista minable con
    los datos que se generan con el uso del sistema"""
    #####################
#    import sklearn as sk
#    import numpy as np
    #####################
    target_class_name = 'participants'  #Default class
    feature_names     = ['apparentTemperature', 'precipIntensity','humidity',
                         'summary','pressure'] #Default features
    def __init__(self, phoneNumber,activity):
        """In order to create the vista minable, a phone number with proper
        access to the database must be given, as well as the activity under
        study."""
        self.phoneNumber = phoneNumber
        self.activity    = activity
        self.initHour    = "0" # This initHour is a dummy value, just to start the object. Could I use it to store any useful data on it, like participants are the admins of that activity.
        self.database    = databaseAccess[self.phoneNumber]
        self.timeTuple   = None # (year,month,day,hour,minute)
        try:
           super(VistaMinable, self).__init__(self.database,self.activity,self.initHour)
        except KeyError as e:
           print("Error: Your telephone's number has no access to this system")

    def getData(self):
        """ Returns a dictionary with all weather variables for each initHour
        that is the database for the current week"""
        print("a ver che...")
        from forecastiopy import ForecastIO
        # TODO: A method that will get the weather variables for the activity
        # initHour when the time comes. DONE
        Cordoba = [-31.4173,-64.1833] # TODO: Avoid this hardcoded data
        language= 'es'
        with open("forecast.txt", "r") as file:
            forecastAPI= file.readlines().pop().rstrip('\n')
        _,timeRange = ActivityRegister(
                      self.database,self.activity,self.initHour).periodReport('semanal')
        weatherData = dict()
        timeRange.sort()
        for time in timeRange:
            weatherData[time]                 = dict()
            weatherData[time]['participants'] = ActivityRegister(
                self.database,self.activity,unicode(time)).howMuch()
            fio = ForecastIO.ForecastIO(forecastAPI, latitude=Cordoba[0], longitude=Cordoba[1],lang=language)
            fio.time_url=time.rstrip('0').rstrip('.') #needs to be done couse
            #the api doesn't support floating point time
            forecast = json.loads(fio.http_get(fio.get_url()))
            for key in forecast['currently'].keys():
                weatherData[time][key]=forecast['currently'][key]
#                print(time,key,datos,weatherData[time][key])
            #'summary','apparentTemperature','precipIntensity',
            #'humidity','pressure','precipProbability','windSpeed',
            #'Among others variables'
        setattr(self, 'data',weatherData)

    def createFeatures(self):
        """This method will create two list: the feature list and the target
        class values for that examples. This method can only be called after
        using the getData method, which will retrieve al info from weather cast
        api for the initHour and the number of participants."""
        features     = list()
        target_class = list()
        for time in self.data.keys():
            instance = list()
            for f in self.feature_names: #Get only the features which we chose
                try: instance.append(self.data[time][f])
                except: pass
            target_class.append(self.data[time][self.target_class_name])
            if len(instance) > 0: features.append(instance)
        setattr(self,'features_values',self.np.array(features))
        setattr(self,'target_class_value',self.np.array(target_class))

    def binaryTree(self):
        """This will preprocess all categorical features to numerical values"""
        from sklearn.preprocessing import LabelEncoder
        enc = LabelEncoder()
        #Due to numpy < 1.7 I must convert unicode -> str
        temporary = vm.np.array(map(str,self.features_values[:,3]))
        label_encoder = enc.fit(temporary)
        integer_classes = label_encoder.transform(label_encoder.classes_).reshape(2, 1)
        #El dos es la cantidad de estados (TODO: evitar este valor hardcodeado)
        enc = OneHotEncoder()
        one_hot_encoder = enc.fit(integer_classes)
        num_of_rows = temporary.shape[0]
        t = label_encoder.transform(temporary).reshape(num_of_rows, 1)
        # Second, create a sparse matrix with two columns, each one indicating if the
        # instance belongs to the class
        new_features = one_hot_encoder.transform(t)
        # Add the new features to features_values
        self.features_values = vm.np.concatenate([self.features_values,
                                          new_features.toarray()], axis = 1)
        #Eliminate converted columns
        self.features_values = vm.np.delete(self.features_values, [3], 1)
        # Update feature names
        # (TODO: evitar estos valores hardcodeados):
        feature_names     = ['apparentTemperature', 'precipIntensity','humidity',
                             'pressure','Despejado','Parcialmente Nublado']
        # Now preprocess the target class:
        temporary = vm.np.array(map(str,self.target_class_value))
        self.sk.preprocessing.Binarizer(threshold=5).fit(temporary.reshape(-1,1))
        self.target_class_value = binarizer.transform(temporary)
        # Now do the same for the 'summary' feature, which is a categoric value
        # transformed to a binary vector :
        # First, convert clases to 0-(N-1) integers using label_encoder

        # Convert to numerical values
        self.features_values = self.features_values.astype(float)
        self.target_class_value = self.target_class_value.astype(float)
        # Hacemos cross validation, con el 75\% y 25\% de los datos
        from sklearn.cross_validation import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(self.features_values,
                                                    self.target_class_value,
                                                    test_size=0.25,
                                                    random_state=33)
        # Creamos el árbol de desición
        from sklearn import tree
        clf = tree.DecisionTreeClassifier(criterion='entropy',
                                  max_depth=3,min_samples_leaf=5)
        clf = clf.fit(X_train,y_train)
        # Visualización
        import StringIO
        dot_data = StringIO.StringIO()
        tree.export_graphviz(clf, out_file=dot_data, feature_names=self.feature_names)
        graph = pydot.graph_from_dot_data(dot_data.getvalue())
        graph.write_png('asistencia.png')
        from IPython.core.display import Image
        Image(filename='asistencia.png')
###
