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
	path = "/Users/masotelof/Dropbox/WebScraping/Data"
	files = [file for file in listdir(path) if file.endswith(".dat")]
	hosts= {}
	bookings = []
	for file in files:
		with open(join(path,file), "rb") as fp:
			rooms = pickle.load(fp)
			for room in rooms:
				host = hosts[room["id"]] if room["id"] in hosts else None
				if host is None:
					host = Host(id=room["id"])
				
				host.long = room["long"] if "long" in room else 'null'
				host.lat = room["lat"] if "lat" in room else 'null'
				host.user = room["user"] if "user" in room else 'null'
				host.since = room["since"] if "since" in room else 'null'
				host.kind = room["kind"] if "kind" in room else 'null'
				host.url = room["url"] if "url" in room else 'null'
				host.capacity = room["capacity"] if "capacity" in room else 'null'
					
				booking = Booking(room["id"], datetime.datetime.strptime(file.replace(".dat", ""), "%Y%m%d").strftime("%Y-%m-%d"))
				booking.price = room["price"].replace("Precio:$","").replace(",","") if "price" in room else None
				booking.reviews = room["reviews"] if "reviews" in room else None
				booking.rating = room["rating"] if "rating" in room else None
				
				if booking.price is not None:
					if booking in bookings:
						pos = bookings.index(booking)
						bookings[pos].price = booking.price
						bookings[pos].reviews = booking.reviews
						bookings[pos].rating = booking.rating
					else:
						bookings.append(booking)

				hosts[room["id"]] = host
	
	
	engine = create_engine("sqlite:///hosts.db", echo=False)
	Session = sessionmaker(bind=engine)
	s = Session()

	s.add_all(list(hosts.values()))
	s.add_all(bookings)
	
	'''
	for value in s.query(Host).filter(or_(Host._Host__long == None, Host._Host__lat == None, Host._Host__kind == None)).all():
		print(value)
		print(type(value))
	'''
	s.commit()
	
					
