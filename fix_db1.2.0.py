from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_, and_
from os import listdir
from os.path import isfile, join
from Hosts import *
from ftplib import FTP
import pysftp
import sqlite3
import locale
import pickle
import os
import re
import sys
import getopt

import time
import datetime
from random import uniform
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.firefox.options import Options

locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
repeat = 13

def get_url(state, suburb, checkin, checkout):
	url_base = "https://www.airbnb.mx"
	return f'{url_base}/s/{suburb}--{state}/all?query={suburb}%2C%20{state}&checkin={checkin}&checkout={checkout}&adults=0&children=0&infants=0&guests=0&refinement_paths%5B%5D=%2Fhomes&click_referer=t%3ASEE_ALL%7Csid%3Ac01cd93d-57a0-4baf-8021-105be8185981%7Cst%3AMAGAZINE_HOMES&title_type=MAGAZINE_HOMES&search_type=UNKNOWN'
	
def host_complete(session, hosts):
	try:
		chrome_options = Options()
		# chrome_options.add_argument('--headless')  # Ejecuta en fondo
		chrome_options.add_argument('--window-size=1920x1080')
		chrome_options.add_argument('--auto-open-devtools-for-tabs')
		driver = webdriver.Chrome(options=chrome_options)

		total = len(hosts)
		for (i, host) in enumerate(hosts):
			logging.warning(f'{i}/{total} {host}')
			get_geo(host, driver)
			logging.warning(f'{i}/{total} {host}')
			if i%10 == 0:
				session.commit()

		driver.close()
		return hosts
	except:
		logging.error("Exception occurred", exc_info=True)

def get_geo(room, driver):
	url = f'https://www.airbnb.mx/rooms/{room.id}'
	logging.warning(url)
	
	cont = 0
	while cont<repeat or room.rooms is None or room.capacity is None or room.since is None or room.long is None or room.lat is None:
		try:
			cont +=1
			
			driver.get(url)
			if url.split("?")[0] not in driver.current_url:
				return 
				# break 
			
			time.sleep(uniform(5, 7))
			
			if len(driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")) > 0:
				driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")[0].click()
					
			if room.long is None or room.lat is None:
				for item in driver.find_elements_by_xpath("//*[contains(@src, 'https://maps.googleapis.com/maps/api/staticmap')]"):
					if "center" in item.get_attribute("src"):
						long_lat = item.get_attribute("src").split("center=")[1]
						long_lat = long_lat.split("&")[0].split("%2C")
						room.long = long_lat[1]
						room.lat = long_lat[0]
						break
					
			if room.user is None:
				for item in driver.find_elements_by_xpath("//*[contains(@href, '/users/show')]"):
					room.user = item.get_attribute('href').split("/")[-1]
					break

			html = driver.page_source
			room_soup = bs4.BeautifulSoup(html, 'html.parser')

			if room.since is None:
				for room_host in room_soup.findAll('div', {'class': '_10ejfg4u'}):
					for room_since in room_host.findAll('div', {'class': '_czm8crp'}):
						if "Se registró en" in room_since.text:
							if "·" in room_since.text:
								room.since = room_since.text.split("·")[1].replace("Se registró en", "").strip()
							else:
								room.since = room_since.text.replace("Se registró en", "").strip()

			if room.capacity is None or room.rooms is None:
				for values in room_soup.findAll('div', {'class': '_1gw6tte'}):
					for capacities in values.findAll('div', {'class': '_hgs47m'}):
						for capacity in capacities.findChildren('div', recursive=True):
							if "huéspedes" in capacity.text or "huésped" in capacity.text:
								for info in capacity.text.split("·"):
									if room.capacity is not None and room.rooms is not None:
										break
										
									if "hués" in info:
										if room.capacity is None:
											room.capacity = re.findall("\d+", str(info))[0]
									if "habita" in info:
										if room.rooms is None:
											room.rooms = re.findall("\d+", str(info))[0]
										
		except:
			logging.error("Exception occurred", exc_info=True)
			
	logging.warning(room)

def save_file_sftp(host, username, password, file, src_path, dest_path):
    try:
        with pysftp.Connection(host, username=username, password=password) as sftp:
            with sftp.cd(dest_path):
                sftp.put(os.path.join(src_path, file))
    except:
        logging.error("Exception occurred", exc_info=True)

def arguments(argv=sys.argv):
    argIn = {}
    try:
        opts, args = getopt.getopt(argv[1:], "h:i:o:u:s:M:m:O:p:P:U:H:C:",
                                   ["checkin=", "checkout=", "suburb=", "state=", "maxprice=", "minprice=", "outfile=",
                                    "pages=", "path=", "host=", "username=", "password="])
        for opt, arg in opts:
            if opt == "-h":
                print(" ".join(str(val) for val in argv[
                                                   :1]) + " -i <checkin date> -o <checkout date> -u <suburb> -s <state> -M <max price> -m <min price> -O <out file> -p <pages> -P <path> -H <host> -C <password> -U <username>,")
                sys.exit()
            elif opt in ("-i", "--checkin"):
                argIn['checkin'] = arg
            elif opt in ("-o", "--checkout"):
                argIn['checkout'] = arg
            elif opt in ("-u", "--suburb"):
                argIn['suburb'] = arg
            elif opt in ("-s", "--state"):
                argIn['state'] = arg
            elif opt in ("-M", "--maxprice"):
                argIn['maxprice'] = arg.strip().lower()
            elif opt in ("-m", "--minprice"):
                argIn['minprice'] = arg.strip().lower()
            elif opt in ("-O", "--outfile"):
                argIn['outfile'] = arg
            elif opt in ("-p", "--pages"):
                argIn['pages'] = int(arg)
            elif opt in ("-P", "--path"):
                argIn['path'] = arg
            elif opt in ("-H", "--host"):
                argIn['host'] = arg
            elif opt in ("-U", "--username"):
                argIn['username'] = arg
            elif opt in ("-C", "--password"):
                argIn['password'] = arg

        if 'checkin' not in argIn:
            argIn['checkin'] = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        if 'checkout' not in argIn:
            argIn['checkout'] = (datetime.datetime.strptime(argIn['checkin'], "%Y-%m-%d") + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
        if 'state' not in argIn:
            argIn['state'] = "Guanajuato"
        if 'suburb' not in argIn:
            argIn['suburb'] = "Guanajuato"
        if 'minprice' not in argIn:
            argIn['minprice'] = None
        if 'maxprice' not in argIn:
            argIn['maxprice'] = None
        if 'outfile' not in argIn:
            argIn['outfile'] = "{}.dat".format(datetime.datetime.now().strftime("%Y%m%d"))
        if 'pages' not in argIn:
            argIn['pages'] = None
        if 'path' not in argIn:
            argIn['path'] = os.getcwd()
        if 'host' not in argIn:
            argIn['host'] = "www.ia-ugto.mx"
        if 'username' not in argIn:
            argIn['username'] = "iaugtomx"
        if 'password' not in argIn:
            argIn['password'] = "74g1k7GicM"

    except getopt.GetoptError:
        print(" ".join(str(val)
                       for val in argv[
                                  :1]) + " -i <checkin date> -o <checkout date> -u <suburb> -s <state> -M <max price> -m <min price> -O <out file> -p <pages> -P <path> -H <host> -C <password> -U <username>,")
        sys.exit(2)
    except:
        logging.error("Exception occurred", exc_info=True)
        sys.exit(2)

    return argIn

if __name__ == "__main__":
	try:
		args = arguments()
		db = "hosts.db"
		log_file = 'webscraping_fix.log'
		path = args['path']

		engine = create_engine("sqlite:///hosts.db", echo=False)
		Session = sessionmaker(bind=engine)
		session_save = Session()
		
		# logging.basicConfig(level=logging.ERROR)
		logging.basicConfig(level=logging.WARNING, filename=os.path.join(path, log_file), format='%(asctime)s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w')
		# hosts = [host for host in session_save.query(Host).filter(or_(Host._Host__long == None, Host._Host__lat == None, Host._Host__user == None, Host._Host__rooms == None, Host._Host__capacity == None, Host._Host__since == None)).all() ] 
		hosts = [host for host in session_save.query(Host).filter(or_(Host._Host__long == None, Host._Host__lat == None, Host._Host__user == None, Host._Host__rooms == None, Host._Host__capacity == None, Host._Host__since == None)).all() ] 

		print(len(hosts))

		host_complete(session_save, hosts)
		
		session_save.commit()

		host = "10.11.17.140"
		username = "masotelof"
		password = "m@sFcrF2204"
		save_file_sftp(host, username, password, db, path, "DatosSotelo/AirBNB")
		save_file_sftp(host, username, password, log_file, path, "DatosSotelo/AirBNB")
	except:
		logging.error("Exception occurred", exc_info=True)