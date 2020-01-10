from sqlalchemy import Column, ForeignKey, Integer, String, Float, Boolean, null
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import datetime
import logging

Base = declarative_base()


class State(Base):
	__tablename__ = "state"
	__id = Column('id_state', Integer, primary_key=True)
	__desc = Column('desc', String, nullable=False)
	suburbs = relationship('Suburb', backref='state', lazy=True)

	def __init__(self, id=None, desc=None):
		self.__id = id
		self.__desc = desc

	@property
	def id(self):
		return self.__id

	@property
	def desc(self):
		return self.__desc

	@desc.setter
	def desc(self, value):
		if value is not None:
			self.__desc = value

	def __eq__(self, other):
		return self.__desc == other.__desc

	def __str__(self):
		return f'desc={self.__desc}'


class Suburb(Base):
	__tablename__ = "suburb"
	__id = Column('id_suburb', Integer, primary_key=True)
	__state = Column('id_state', Integer, ForeignKey('state.id_state'), primary_key=True)
	__desc = Column('desc', String, nullable=False)
	__active = Column('active', Integer, nullable=False)
	__long = Column('long', Float, nullable=True)
	__lat = Column('lat', Float, nullable=True)
	hosts = relationship('Host', backref='suburb', lazy=True)

	def __init__(self, id=None, state=None, desc=None, long=None, lat=None, active=1):
		self.__id = id
		self.__state = state
		self.__desc = desc
		self.__active = active
		self.__long = long
		self.__lat = lat

	@property
	def id(self):
		return self.__id
	
	@property
	def state(self):
		return self.__state

	@state.setter
	def state(self, value):
		if value is not None:
			self.__state = value
	
	@property
	def desc(self):
		return self.__desc

	@desc.setter
	def desc(self, value):
		if value is not None:
			self.__desc = value
	
	@property
	def active(self):
		return self.__active

	@active.setter
	def active(self, value):
		if value is not None:
			self.__active = value

	@property
	def long(self):
		return self.__long

	@long.setter
	def long(self, value):
		if value is not None:
			self.__long = value

	@property
	def lat(self):
		return self.__lat

	@lat.setter
	def lat(self, value):
		if value is not None:
			self.__lat = value

	def __eq__(self, other):
		return self.__desc == other.__desc

	def __str__(self):
		return f' state={self.__state} desc={self.__desc}'


class Type(Base):
	__tablename__ = "type"
	__id = Column('id_type', Integer, primary_key=True)
	__desc = Column('desc', String, nullable=False)
	kinds = relationship('Kind', backref='type', lazy=True)

	def __init__(self, id=None, desc=None):
		self.__id = id
		self.__desc = desc

	@property
	def id(self):
		return self.__id

	@property
	def desc(self):
		return self.__desc

	@desc.setter
	def desc(self, value):
		if value is not None:
			self.__desc = value

	def __eq__(self, other):
		return self.__desc == other.__desc

	def __str__(self):
		return f'desc={self.__desc}'


class Kind(Base):
	__tablename__ = "kind"
	__id = Column('id_kind', Integer, primary_key=True)
	__desc = Column('desc', String, nullable=False)
	__type = Column('id_type', Integer, ForeignKey('type.id_type'), nullable=False)
	hosts = relationship('Host', backref='kind', lazy=True)

	def __init__(self, id=None, desc=None, type=None):
		self.__id = id
		self.__desc = desc
		self.__type = type

	@property
	def id(self):
		return self.__id

	@property
	def desc(self):
		return self.__desc

	@desc.setter
	def desc(self, value):
		if value is not None:
			self.__desc = value

	@property
	def type(self):
		return self.__type

	@type.setter
	def type(self, value):
		if value is not None:
			self.__type = value

	def __eq__(self, other):
		return self.__desc == other.__desc

	def __str__(self):
		return f'desc={self.__desc}'


class Booking(Base):
	__tablename__ = "booking"
	__id = Column('id_host', String, ForeignKey('host.id_host'), primary_key=True)
	__date = Column('date', String, primary_key=True)
	__price = Column('price', Float, nullable=False)
	__rating = Column('rating', Float, nullable=True)
	__reviews = Column('reviews', Float, nullable=True)
		
	def __init__(self, id=None, date=None, price=None, rating=None, reviews=None):
		self.__id = id
		self.__date = date
		try:
			self.__price = float(price)
		except:
			pass
		
		try:
			self.__rating = float(rating)
		except:
			pass
		
		try:
			self.__reviews = float(reviews)
		except:
			pass

	@property
	def id(self):
		return self.__id
			
	@property
	def date(self):
		return self.__date
		
	@property
	def price(self):
		return self.__price
	
	@price.setter
	def price(self, value):
		if value is not None:
			try:
				self.__price = float(value)
			except:
				pass
		
	@property
	def reviews(self):
		return self.__reviews
	
	@reviews.setter
	def reviews(self, value):
		if value is not None:
			try:
				self.__reviews = float(value)
			except:
				pass

	@property
	def rating(self):
		return self.__rating
	
	@rating.setter
	def rating(self, value):
		if value is not None:
			try:
				self.__rating = float(value)
			except:
				pass
			
	def __eq__(self, other):
		return self.__id == other.__id and self.__date == other.__date
		
	def __str__(self):
		return f'date={self.__date} price={self.__price} reviews={self.__reviews} rating={self.__rating}'
		

class Host(Base):
	__tablename__ = "host"
	__id = Column('id_host', String, primary_key=True)
	__suburb = Column('id_suburb', Integer, ForeignKey('suburb.id_suburb'), nullable=False)
	__long = Column('long', Float, nullable=True)
	__lat = Column('lat', Float, nullable=True)
	__user = Column('user', String, nullable=True)
	__since = Column('since', String, nullable=True)
	__kind = Column('id_kind', Integer, ForeignKey('kind.id_kind'), nullable=False)
	__rooms = Column('rooms', Integer, nullable=True)
	__capacity = Column('capacity', Integer, nullable=True)
	bookings = relationship('Booking', backref='host', lazy=True)
	
	def __init__(self, id=None, suburb=None, long=None, lat=None, user=None, since=None, kind=None, capacity=None, rooms=None, url=None):
		self.__id = id
		self.__suburb = suburb
		
		try:
			self.__long = float(long)
		except:
			self.__long = None
		
		try:
			self.__lat = float(lat)
		except:
			self.__lat = None
		
		try:
			self.__user = int(user)
		except:
			self.__user = None
			
		self.__since = since
		
		try:
			self.__kind = int(kind)
		except:
			self.__kind = None
			
		try:
			self.__rooms =  int(rooms)
		except:
			self.__rooms = None
			
		try:
			self.__capacity = int(capacity)
		except:
			self.__capacity = None
		self.__url = url
	
	@property
	def id(self):
		return self.__id

	@property
	def suburb(self):
		return self.__suburb

	@suburb.setter
	def suburb(self, value):
		if value is not None:
			self.__suburb = value

	@property
	def long(self):
		return self.__long
	
	@long.setter
	def long(self, value):
		if value is not None:
			try:
				self.__long = float(value)
			except:
				pass
		
	@property
	def lat(self):
		return self.__lat
		
	@lat.setter
	def lat(self, value):
		if value is not None:
			try:
				self.__lat = float(value)
			except:
				pass
		
	@property
	def user(self):
		return self.__user
	
	@user.setter
	def user(self, value):
		if value is not None:
			try:
				self.__user = int(value)
			except:
				pass
		
	@property
	def since(self):
		return self.__since
	
	@since.setter
	def since(self, value):
		if value is not "null" and value is not null and value is not None and value != "null":
			try:
				self.__since = datetime.datetime.strptime(value, "%Y-%m-%d")
			except:
				self.__since = datetime.datetime.strptime(value, "%B de %Y").strftime("%Y-%m-%d")

	@property
	def kind(self):
		return self.__kind
	
	@kind.setter
	def kind(self, value):
		if value is not None:
			try:
				self.__kind = int(value)
			except:
				pass
		
	@property
	def capacity(self):
		return self.__capacity
	
	@capacity.setter
	def capacity(self, value):
		if value is not None:
			try:
				self.__capacity = int(value)
			except:
				pass
	
	@property
	def rooms(self):
		return self.__rooms
	
	@rooms.setter
	def rooms(self, value):
		if value is not None:
			try:
				self.__rooms = int(value)
			except:
				pass

	@property
	def url(self):
		return self.__url
	
	@url.setter
	def url(self, value):
		if value is not None:
			self.__url = value
		
	def __eq__(self, other):
		return self.__id == other.__id
					
	def __str__(self):
		return f'[ "id": "{self.__id}", "suburb": "{self.__suburb}", "user": "{self.__user}", "since":"{self.__since}", "longlat":[{self.__lat}, {self.__long}], "kind": "{self.__kind}", "capacity": "{self.__capacity}", "rooms": "{self.__rooms}"]'

