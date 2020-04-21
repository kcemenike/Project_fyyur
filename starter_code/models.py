from app import db
import datetime

class Venue(db.Model):
  __tablename__ = 'venues'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  city = db.Column(db.String(50))
  state = db.Column(db.String(50))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(50))
  genres = db.Column(db.ARRAY(db.String)) # Array object for holding multiple arrays
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref='venue', lazy='dynamic')

  def __repr__(self):
    return f"<Venue: {self.id} {self.name}>"

  def __init__(self, name, city, state, address=None, phone=None, image_link=None, facebook_link=None, website=None, seeking_talent=False, seeking_description=None):
    self.name = name
    self.city = city
    self.state = state
    self.address =address
    self.phone = phone
    self.image_link = image_link
    self.facebook_link = facebook_link
    self.website = website
    self.seeking_talent = seeking_talent
    self.seeking_description = seeking_description

  # decorator that allows to view a venue with number of upcoming shows
  @property
  def format(self):
    return {
      'id' : self.id,
      'name': self.name,
      'no_upcoming_shows': len(Show.query.filter(Show.start_time>datetime.datetime.now()).filter(self.id==Show.venue_id).all())
    }

  @property
  def format_with_shows_count(self):
    # venues.format - city, state, 
    # Venue.format_shows_count (id, name, num_upcoming_shows)
    return {
      'city': self.city,
      'state': self.state,
      'venues': [venue.format for venue in Venue.query.filter(Show.venue_id==self.id).all()]
    }

  @property
  def format_with_shows(self):
    
    return {
      'id' : self.id,
      'name': self.name,
      'genres': self.genres, # [artist.genres for artist in Artist.query.filter(Show.artist_id==Artist.id)],
      'address': self.address,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'image_link': self.image_link,
      'website': self.website,
      'facebook_link': self.facebook_link,
      'seeking_talent': self.seeking_talent,
      'description': self.seeking_description,
      'past_shows': [show.format_with_artist for show in Show.query.filter(Show.venue_id==self.id, Show.start_time<datetime.datetime.now())],
      'past_shows_count': len(Show.query.filter(Show.venue_id==self.id, Show.start_time<datetime.datetime.now()).all()),
      'upcoming_shows':  [show.format_with_artist for show in Show.query.filter(Show.venue_id==self.id, Show.start_time>datetime.datetime.now())],
      'upcoming_shows_count': len(Show.query.filter(Show.venue_id==self.id, Show.start_time>datetime.datetime.now()).all()),
    }

  @property
  def format_with_city_state(self):
    return {
      'city': self.city,
      'state': self.state,
      'venues': [venue.format_with_shows_count for venue in Venue.query.filter(Venue.city==self.city, Venue.state==self.state).all()]
    }

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

#     # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
  __tablename__ = 'artists'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  city = db.Column(db.String(50))
  state = db.Column(db.String(50))
  phone = db.Column(db.String(50))
  genres = db.Column(db.ARRAY(db.String))
  image_link = db.Column(db.String(500))
  website = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref='artist', lazy="dynamic")

  def __init__(self, name, city, state, phone=None, image_link=None, website=None, facebook_link=None, seeking_venue=False, seeking_description=None,  genres=[]):
    self.name = name
    self.city = city
    self.state = state
    self.phone = phone
    self.genres = genres # [genre for genre in list(genres.values())[0]]
    self.image_link = image_link
    self.website = website
    self.facebook_link = facebook_link
    self.seeking_venue = seeking_venue
    self.seeking_description = seeking_description

  @property
  def format(self):
    return {
      'id' : self.id,
      'name': self.name
    }

  @property
  def format_with_shows_venue(self):
    return {
      'id': self.id,
      'name': self.name,
      'genres': self.genres,
      'city': self.city,
      'state': self.state,
      'phone': self.phone,
      'website': self.website,
      'facebook_link': self.facebook_link,
      'seeking_venue': self.seeking_venue,
      'seeking_description': self.seeking_description,
      'image_link': self.image_link,
      'past_shows': [show.format_with_venue for show in Show.query.filter(Show.start_time<datetime.datetime.now()).all()],
      'upcoming_shows': [show.format_with_venue for show in Show.query.filter(Show.start_time>datetime.datetime.now()).all()],
      'past_shows_count': len(Show.query.filter(Show.start_time<datetime.datetime.now()).all()),
      'upcoming_shows_count': len(Show.query.filter(Show.start_time>datetime.datetime.now()).all())
    }


  def __repr__(self):
    return f"<Artist: {self.id} {self.name}>"

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime())
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

  def __repr__(self):
    return f"<Show: {self.artist_id} {self.venue_id}, {self.start_time}>"

  @property
  def format(self):
    return {
      'start_time': self.start_time,
      'artist_id': self.artist_id,
      'venue_id': self.venue_id
    }

  @property
  def format_with_artist(self):
    # artist_id, artist_name, artist_image_link, start_time
    return {
      'artist_id': self.artist_id,
      'artist_name' : Artist.query.filter(Artist.id==self.artist_id).one_or_none().name,
      'artist_image_link': Artist.query.filter(Artist.id==self.artist_id).one_or_none().image_link,
      'start_time': datetime.datetime.strftime(self.start_time, "%d-%m-%Y %H:%M:%S")
    }

    
  # shows.format_with_artist_venue = venue_id, venue_name, artist_id, artist_name, artist_image_link, start_time
  @property
  def format_with_artist_venue(self):
    return {
      'venue_id':self.venue_id, # self.venue_id
      'venue_name': Venue.query.filter(self.venue_id==Venue.id).one_or_none().name, # self.venue_id = Venue.id
      'artist_id': self.artist_id, # self.artist_id
      'artist_name': Artist.query.filter(self.artist_id==Artist.id).one_or_none().name, # self.artist_id = Artist.id
      'artist_image_link': Artist.query.filter(self.artist_id==Artist.id).one_or_none().image_link, #self.artist_id = Artist.id
      'start_time': datetime.datetime.strftime(self.start_time, "%d-%m-%Y %H:%M:%S") # self.start_time
    }

  # shows.format_with_venue (venue_id, venue_name, venue_image_link, start_time)
  @property
  def format_with_venue(self):
    return {
      'venue_id': self.venue_id, # self.venue_id
      'venue_name': Venue.query.filter(self.venue_id==Venue.id).one_or_none().name, # self.venue_id == venue.id
      'venue_image_link': Venue.query.filter(self.venue_id==Venue.id).one_or_none().image_link, # self.venue_id == venue.id
      'start_time': datetime.datetime.strftime(self.start_time, "%d-%m-%Y %H:%M:%S") # self.start_time
    }

  def __init__(self, artist_id, venue_id, start_time):
    self.start_time = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    self.artist_id = artist_id
    self.venue_id = venue_id

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()
