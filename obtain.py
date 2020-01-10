from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_
from os import listdir
from os.path import isfile, join
from Hosts import *
import sqlite3
import locale
import pickle

locale.setlocale(locale.LC_ALL, "es_Es")

if __name__ == "__main__":
	engine_old = create_engine("sqlite:////Users/masotelof/Dropbox/WebScraping/Hosts.db", echo=False)
	Session_old = sessionmaker(bind=engine_old)
	session_old = Session_old()
	
	engine_new = create_engine("sqlite:///hosts.db", echo=False)
	Session_new = sessionmaker(bind=engine_new)
	session_new = Session_new()
	
	hosts_old = [value for value in session_old.query(Host).all()]
	hosts_new = [value for value in session_new.query(Host).all()]
	
	for (pos_new, host_new) in enumerate(hosts_new):
		if host_new in hosts_old:
			pos_old = hosts_old.index(host_new)
			hosts_new[pos_new].long = hosts_old[pos_old].long
			hosts_new[pos_new].lat = hosts_old[pos_old].lat
			hosts_new[pos_new].user = hosts_old[pos_old].user
			hosts_new[pos_new].since = hosts_old[pos_old].since
			hosts_new[pos_new].kind = hosts_old[pos_old].kind
			
	session_new.commit()
			
	
	
	