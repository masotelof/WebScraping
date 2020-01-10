from utils import arguments, save_file_ftp, save_file_sftp
import datetime
import getopt
import logging
import os
import pickle
import re
import sys
import time
import locale
from random import uniform

import sqlite3
# imports to sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.sql.expression import desc

# import to Host 
from Hosts import Host, Booking, State, Suburb, Kind, Type

# imports to selenium
import bs4
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

url_base = "https://www.airbnb.mx"
locale.setlocale(locale.LC_ALL, "es_ES.UTF-8")
repeat = 13

def connectDB(path, db):
    engine = create_engine(f'sqlite:///{os.path.join(path, db)}', echo=False)
    Session = sessionmaker(bind=engine)
    return Session()


def getUrl(state, suburb, checkin, checkout):
    return f'{url_base}/s/{suburb}--{state}/all?query={suburb}%2C%20{state}&checkin={checkin}&checkout={checkout}&adults=0&children=0&infants=0&guests=0&refinement_paths%5B%5D=%2Fhomes&click_referer=t%3ASEE_ALL%7Csid%3Ac01cd93d-57a0-4baf-8021-105be8185981%7Cst%3AMAGAZINE_HOMES&title_type=MAGAZINE_HOMES&search_type=UNKNOWN'

def getDriver():
    try:
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # Ejecuta en fondo
        # chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--start-maximized')  
        chrome_options.add_argument('--auto-open-devtools-for-tabs')
        
        return webdriver.Chrome(options=chrome_options)
    except:
        logging.error("Exception occurred", exc_info=True)
        return None 

def getHostGeo(driver, host):
    attributes = ['long', 'lat', 'user', 'since']
    #logging.warning(host["url"])
    cont = 1
    
    while cont<=repeat:
        try:
            logging.warning(f'Attempting {cont}/{repeat}')
            cont +=1
            
            driver.get(host["url"])
            if host["url"].split("?")[0] not in driver.current_url:
                break 
            
            time.sleep(uniform(3, 5))
            
            try:
                if len(driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")) > 0:
                    driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")[0].click()
            except:
                pass
                    
            if host['long'] is None or host['lat'] is None:
                for item in driver.find_elements_by_xpath("//*[contains(@src, 'https://maps.googleapis.com/maps/api/staticmap')]"):
                    if "center" in item.get_attribute("src"):
                        long_lat = item.get_attribute("src").split("center=")[1].split("&")[0].split("%2C")
                        host['long'] = long_lat[1]
                        host['lat'] = long_lat[0]
                        break
                    
            if host["user"] is None:
                for item in driver.find_elements_by_xpath("//*[contains(@href, '/users/show')]"):
                    host["user"] = item.get_attribute('href').split("/")[-1]
                    break


            html = driver.page_source
            room_soup = bs4.BeautifulSoup(html, 'html.parser')
    
            if host['long'] is None or host['lat'] is None:
                for room_longlat in room_soup.findAll('img', {'data-veloute': 'map/GoogleMapStatic'}):
                     if "center" in room_longlat["src"]:
                        long_lat = room_longlat["src"].split("center=")[1].split("&")[0].split("%2C")
                        host['long'] = long_lat[1]
                        host['lat'] = long_lat[0]
                        break
                
            if host['since'] is None:
                for room_host in room_soup.findAll('div', {'class': '_10ejfg4u'}):
                    for room_since in room_host.findAll('div', {'class': '_czm8crp'}):
                        if "Se registró en" in room_since.text:
                            if "·" in room_since.text:
                                host['since'] = room_since.text.split("·")[1].replace("Se registró en", "").strip()
                            else:
                                host['since'] = room_since.text.replace("Se registró en", "").strip()

                for room_host in room_soup.findAll('div', {'class': '_f47qa6'}):
                    for room_since in room_host.findAll('div', {'class': '_5vw6iv'}):
                        if "Se registró en" in room_since.text:
                            if "·" in room_since.text:
                                host['since'] = room_since.text.split("·")[1].replace("Se registró en", "").strip()
                            else:
                                host['since'] = room_since.text.replace("Se registró en", "").strip()
    
                if host["since"] is not None:
                    try:
                        datetime.datetime.strptime(host["since"], '%Y-%m-%d')
                    except ValueError:
                        host["since"] = datetime.datetime.strptime(host["since"], "%B de %Y").strftime("%Y-%m-%d")
            
            values_notNone = sum([0 if host[attribute] is None else 1 for attribute in attributes])
            if values_notNone == len(attributes):
                break
                
        except:
            logging.error("Exception occurred", exc_info=True)
            
    logging.warning(host)

def getHosts(soup, suburb, checkin):
    hosts = []
    try:
        for (cont, data) in enumerate(soup.findAll('div', {'itemprop': "itemListElement"})):
            try:
                logging.info(f'Processing host {cont}')
                
                host = {'id': None, 'checkin': None, 'long': None, 'lat': None, 'price': None, 'info': None, 'url': "", 'capacity': None, 'kind': None, 'rating': None, 'evaluations': None,  'rooms': None, "user":None, 'since':None}
                
                host['id'] = data.findAll('a',  href=True)[0]['target'].split("_")[-1]
                host['checkin'] = checkin
                
                host['url'] = '{}{}'.format(url_base, data.findAll('a',  href=True)[0]['href'])
                if host['url'] is None or host['url'] is '' or "plus" in host['url']:
                    continue
                try:
                    for values in data.findAll('span',  {'class': '_krjbj'}):
                        if "Valoración" in values.text:
                            host['rating'] = values.text.replace("Valoración", "").split(" de ")[0].strip()
                            break
                    host['evaluations'] = data.find('span',  {'class': '_14e6cbz'}).text.replace("(","").replace(")","")
                except:
                    pass
                    
                for values in data.findAll('span',  {'class': '_1p7iugi'}):
                    if "Precio" in values.text and "MXN" in values.text:
                        host['price'] = re.findall("\d+\.\d+|\d+", str(values.text).split("$")[-1].split("MXN")[0].replace(",",""))[0]
                        
                if host['price'] is None:
                    continue

                try:
                    host['kind'] = data.findAll('div', {'class': '_1q6rrz5'})[0].text if "·" not in data.findAll('div', {'class': '_1q6rrz5'})[0].text else data.findAll('div', {'class': '_1q6rrz5'})[0].text.split("·")[0]
                except:
                    host['kind'] = data.findAll('div', {'class': '_1j3840rv'})[0].text if "·" not in data.findAll('div', {'class': '_1j3840rv'})[0].text else data.findAll('div', {'class': '_1j3840rv'})[0].text.split("·")[0]
                
                for info in data.findAll('div', {'class': '_1s7voim'})[0].text.split("·"):
                    if "hués" in info:
                        host['capacity'] = [int(s) for s in info.split() if s.isdigit()][0]
                    if "habita" in info:
                        host['rooms'] = [int(s) for s in info.split() if s.isdigit()][0]
                
                # host['info'] = [ info for info in data.findAll('div', {'class': '_1s7voim'})[1].text.split("·")]
        
                hosts.append(host)
            except:
                logging.error("Exception occurred", exc_info=True)
    except:
        logging.error("Exception occurred", exc_info=True)

    return hosts

def getHostsbyPages(driver, state, suburb, checkin, checkout):
    hosts = []
    
    if driver is None:
        return hosts

    try:
        url = getUrl(state, suburb, checkin, checkout)
        logging.info(url)
        driver.get(url)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(uniform(4, 4.5))

        try:
            if len(driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")) > 0:
                driver.find_elements_by_xpath("//button[@class='optanon-allow-all accept-cookies-button']")[0].click()
        except:
            pass

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')

        # change the whay to obtain the page number
        pages = [int(data.text) for data in soup.findAll('div', {'class': '_1bdke5s'})]
        page_number = max(pages) if pages else 0

        if page_number == 0:
            return hosts

        for number in range(1, page_number + 1):
            logging.warning(f'Processing page {number}')
            logging.info(f'URL {url}')

            if number!=1:
                offset = (number - 1) * 18
                page = url + '&items_offset=' + str(offset)

                driver.get(page)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # time.sleep(uniform(2, 2.5))

                html = driver.page_source
                soup = bs4.BeautifulSoup(html, 'html.parser')
            
            hosts += getHosts(soup, suburb, checkin)
    except:
        logging.error("Exception occurred", exc_info=True)
        
    return hosts

def saveHostsDB(driver, session, hosts):
    try:
        total = len(hosts)
        for i, _host in enumerate(hosts):
            logging.warning(f'Processing host {i}/{total}')
            try:
                # check for kinds
                if session.query(Kind).filter(Kind._Kind__desc == _host["kind"]).count() > 0:
                    kind = session.query(Kind).filter(Kind._Kind__desc == _host["kind"]).one()
                else:
                    last_kind = session.query(Kind).order_by(desc(Kind._Kind__id))[0]
                    kind = Kind(last_kind.id+1, _host["kind"], 1)
                    session.add(kind)
                
                host_id = _host['id']
                # check for hosts
                if session.query(Host).filter(Host._Host__id == host_id).count() > 0:
                    host = session.query(Host).filter(Host._Host__id == host_id).one()
                    host.suburb = suburb
                    if host.long is None or host.lat is None or host.user is None or host.since is None:
                        getHostGeo(driver, _host)
                    host.long = _host["long"]
                    host.lat = _host["lat"]
                    host.user = _host["user"]
                    host.since = _host["since"]
                    host.rooms = _host["rooms"]
                    host.kind = kind
                    host.capacity = _host["capacity"]
                else:
                    host = Host(host_id)
                    host.suburb = suburb
                    getHostGeo(driver, _host)
                    host.long = _host["long"]
                    host.lat = _host["lat"]
                    host.user = _host["user"]
                    host.since = _host["since"]
                    host.rooms = _host["rooms"]
                    host.kind = kind
                    host.capacity = _host["capacity"]

                    session.add(host)

                if session.query(Booking).filter(and_(Booking._Booking__id == host_id, Booking._Booking__date == _host['checkin'])).count() > 0:
                    booking = session.query(Booking).filter(and_(Booking._Booking__id == host_id, Booking._Booking__date == _host['checkin'])).one()
                    booking.price = _host['price']
                    booking.rating = _host['rating']
                    booking.reviews = _host['evaluations']
                else:
                    booking = Booking(host_id, _host['checkin'])
                    booking.price = _host['price']
                    booking.rating = _host['rating']
                    booking.reviews = _host['evaluations']
                    session.add(booking)

                session.commit()
                logging.info(host)
            except:
                logging.error(_host)
                logging.error("Exception occurred", exc_info=True)

    except:
        logging.error("Exception occurred", exc_info=True)

if __name__ == "__main__":
    try:
        args = arguments()
        checkin = args['checkin']
        checkout = args['checkout']
        max_price = args['maxprice']
        min_price = args['minprice']
        num_pages = args['pages']
        path = args['path']

        host = args['host']
        username = args['username']
        password = args['password']
        db = "hosts.db"
        log_file = 'webscraping.log'

        # logging.basicConfig(level=logging.WARNING, filename=os.path.join(path, log_file) , format='%(asctime)s :: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w+')
        logging.basicConfig(level=logging.WARNING)
        logging.info(f'URL Base: {url_base}')

        session = connectDB(path, db)

        driver = getDriver()
        #driver.fullscreen_window()
        for state in session.query(State).join(Suburb).filter(Suburb._Suburb__active == 1).all():
            for suburb in state.suburbs:
                if suburb.active==0:
                    continue

                logging.warning(f'{state.desc} - {suburb.desc}')
                start = time.time()

                hosts = getHostsbyPages(driver, state.desc, suburb.desc, checkin, checkout)
                saveHostsDB(driver, session, hosts)

                logging.warning("Time {}".format(time.time()-start))
                logging.warning("-"*40)
            session.commit()
        driver.close()
        session.close()
        
        save_file_ftp(host, username, password, db, path, "public_html/turismo")
        logging.warning("File Uploaded to the ftp server")
        logging.warning("-"*40)
        
        
        host = "10.11.17.140"
        username = "masotelof"
        password = "m@sFcrF2204"
        save_file_sftp(host, username, password, log_file, path, "DatosSotelo/AirBNB")
        save_file_sftp(host, username, password, db, path, "DatosSotelo/AirBNB")
        logging.warning("-"*40)
        logging.warning("File Uploaded to the sftp server")
    except Exception as Err:
        print(Err)
        logging.error("Exception occurred", exc_info=True)