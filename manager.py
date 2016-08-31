#!/usr/bin/python
# coding: latin-1
import json
import locale
# This should be tied to a configuration file:
locale.setlocale(locale.LC_ALL,'es_AR.utf8')
import dbapi.py
# TODO: Crear un método que cancele un turno, entre los reservados por la persona. 
# TODO: Crear método que reserve turno y descuente crédito. 
# TODO: Crear un método que cree nuevas actividades a partir de una lista con el siguiente formato:
