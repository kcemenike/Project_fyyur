#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import *
from flask_migrate import Migrate
from flask_cors import CORS
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
csrf = CSRFProtect()
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)
csrf.init_app(app)


@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,-Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
  return response

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET','POST'])
def venues():
  # print(body)
  if request.method == 'POST':
    body = request.get_json()
    if 'name' in body and 'city' in body and 'state' in body:
      name=body['name']
      city=body['city']
      state=body['state']
      address=body['address'] if 'address' in body else None
      phone=body['phone'] if 'phone' in body else None
      image_link=body['image_link'] if 'image_link' in body else None
      facebook_link=body['facebook_link'] if 'facebook_link' in body else "https://facebook.com"
      website=body['website'] if 'website' in body else "https://pydata.co"
      seeking_talent=bool(body['seeking_talent']) if 'seeking_talent' in body else False
      seeking_description=body['seeking_description'] if 'seeking_description' in body else None

      # create venue item and insert into database
      venue = Venue(name, city, state, address, phone, image_link, facebook_link, website, seeking_talent, seeking_description)
      venue.insert()
    else:
      abort(422)
  elif request.method == 'GET':
    data = []
    city_state = ''
    # Group by city and state (and id of course)
    for venue in Venue.query.group_by(Venue.id, Venue.state, Venue.city).all():
      if city_state == venue.city + venue.state:
        data[len(data)-1]['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(venue.shows.filter(Show.start_time > datetime.datetime.now()).all())
        })
      else:
        city_state = venue.city + venue.state
        data.append({
          'city': venue.city,
          'state': venue.state,
          'venues': [{
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(venue.shows.filter(Show.start_time > datetime.datetime.now()).all())
            }]
          })
  return render_template('pages/venues.html', areas=data)

  # return jsonify({
  #   'success': True,
  #   'venues': data
  # })

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venue_query = Venue.query.filter(Venue.name.ilike('%'+request.form['search_term']+'%'))
  venues = [venue.format for venue in venue_query]
  response = {
    'count': len(venues),
    'data': venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id).format_with_shows
  # return jsonify({
  #   'success': True,
  #   'data': data
  # })
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  body = VenueForm(request.form)
  if not body.validate():
    flash(body.errors)
    abort(404)
  if 'name' in body and 'city' in body and 'state' in body:
    name=body['name']
    city=body['city']
    state=body['state']
    address=body['address'] if 'address' in body else None
    phone=body['phone'] if 'phone' in body else None
    image_link=body['image_link'] if 'image_link' in body else None
    facebook_link=body['facebook_link'] if 'facebook_link' in body else "https://facebook.com"
    website=body['website'] if 'website' in body else "https://pydata.co"
    seeking_talent=bool(body['seeking_talent']) if 'seeking_talent' in body else False
    seeking_description=body['seeking_description'] if 'seeking_description' in body else None

    # Create new venue from request data and insert into database
    venue = Venue(name, city, state, address, phone, image_link, facebook_link, website, seeking_talent, seeking_description)
    venue.insert()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(422)
    
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  venue = Venue.query.get(venue_id)
  try:
    venue.delete()
  except:
    db.session.rollback()
    abort(422)
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET', 'POST'])
def artists():
  # TODO: replace with real data returned from querying the database
  if request.method == 'POST':
    body = request.get_json()
    if 'name' in body and 'city' in body and 'state' in body:
      artist = Artist(
        name = body['name'],
        city = body['city'],
        state = body['state'],
        phone = body['phone'] if 'phone' in body else None,
        image_link = body['image_link'] if 'image_link' in body else None,
        facebook_link = body['facebook_link'] if 'facebook_link' in body else None,
        website = body['website'] if 'website' in body else None,
        seeking_venue = bool(body['seeking_venue']) if 'seeking_venue' in body else None,
        genres = body['genres'] if 'genres' in body else []
      )
      artist.insert()
    return jsonify({
      'success': True,
      'artists': [artist.format for artist in Artist.query.all()]
    })
  elif request.method == 'GET':
    data =  [artist.format for artist in Artist.query.all()]
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_results = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term') + '%')).all()
  data = [artist.format for artist in search_results]
  response = {
    'count': len(search_results),
    'data': data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  try:
    data = Artist.query.get(artist_id).format_with_shows_venue
    return render_template('pages/show_artist.html', artist=data)
  except:
    abort(404)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    abort(404)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  body = request.form
  form = ArtistForm(body)
  artist = Artist.query.get(artist_id)
  try:
    if form.validate():
      if 'name' in body and 'city' in body and 'state' in body:
        artist.name = body['name']
        artist.city = body['city']
        artist.state = body['state']
        artist.phone = body['phone'] if 'phone' in body and body['phone'] != '' else artist.phone
        print(artist.phone)
        artist.image_link = body['image_link'] if 'image_link' in body and body['image_link'] != '' else artist.image_link
        artist.facebook_link = body['facebook_link'] if 'facebook_link' in body and body['facebook_link'] != '' else artist.facebook_link
        artist.website = body['website'] if 'website' in body and body['website'] != '' else artist.website
        artist.seeking_venue = bool(body['seeking_venue']) if 'seeking_venue' in body and body['seeking_venue'] != '' else artist.seeking_venue
        artist.genres = body['genres'] if 'genres' in body and body['genres'] != [] else artist.genres
      else:
        abort(422)
      try:
        print(artist.format_with_shows_venue)
        artist.insert()
      except:
        print("Failed to insert data into database")
        db.session.rollback()
        flash("Failed to insert edit Artist data")
      # print("success")
      flash("Artist edit successful")
    else:
      print("failed to validate form")
      abort(404)
  except:
    flash(form.errors)
    # print("fail")
    

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  body = request.form
  form = VenueForm(body)
  venue = Venue.query.get(venue_id)
  try:
    if form.validate():
      if 'name' in body and 'city' in body and 'state' in body:
        venue.name = body['name']
        venue.city = body['city']
        venue.state = body['state']
        venue.address = body['phone'] if 'address' in body and body['address'] != '' else venue.address
        venue.phone = body['phone'] if 'phone' in body and body['phone'] != '' else venue.phone
        venue.image_link = body['image_link'] if 'image_link' in body and body['image_link'] != '' else venue.image_link
        venue.facebook_link = body['facebook_link'] if 'facebook_link' in body and body['facebook_link'] != '' else venue.facebook_link
        venue.website = body['website'] if 'website' in body and body['website'] != '' else venue.website
        venue.seeking_talent = bool(body['seeking_venue']) if 'seeking_venue' in body and body['seeking_venue'] != '' else venue.seeking_talent
        venue.seeking_description = body['seeking_description'] if 'seeking_description' in body and body['seeking_description'] != '' else venue.seeking_description
        venue.genres = body['genres'] if 'genres' in body and body['genres'] != [] else venue.genres
      else:
        abort(422)
      try:
        # print(venue.format_with_shows)
        venue.insert()
      except:
        print("Failed to insert data into database")
        db.session.rollback()
        flash("Failed to insert edit Venue data")
      # print("success")
      flash("Venue edit successful")
    else:
      print("failed to validate form")
      abort(404)
  except:
    flash(form.errors)
    # print("fail")
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  body = request.form
  if 'name' in body and 'city' in body and 'state' in body:
    name=body['name']
    city=body['city']
    state=body['state']
    phone=body['phone'] if 'phone' in body else None
    image_link=body['image_link'] if 'image_link' in body else None
    facebook_link=body['facebook_link'] if 'facebook_link' in body else "https://facebook.com"
    website=body['website'] if 'website' in body else "https://pydata.co"
    seeking_talent=bool(body['seeking_talent']) if 'seeking_talent' in body else False
    seeking_description=body['seeking_description'] if 'seeking_description' in body else None
    genres = body['genres']

    artist = Artist(name, city, state, phone, image_link, website, facebook_link, seeking_talent, seeking_description,  genres)
    artist.insert()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    abort(422)

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows', methods=['GET', 'POST'])
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  if request.method == 'POST':
    body = request.get_json()
    if 'artist_name' in body and 'venue_name' in body and 'start_time' in body:
      show = Show(
        artist_id = Artist.query.filter(Artist.name==body['artist_name']).one_or_none().id,
        venue_id = Venue.query.filter(Venue.name==body['venue_name']).one_or_none().id,
        start_time = body['start_time']
      )
      show.insert()
  elif request.method == 'GET':  
    shows = Show.query.order_by(Show.id).all()
  # return jsonify({
  #   'success': True,
  #   'shows': [show.format for show in shows]
  # })

  data = [show.format_with_artist_venue for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  body = request.form
  if 'artist_name' in body and 'venue_name' in body and 'start_time' in body:
    show = Show(
      artist_id = Artist.query.filter(Artist.name==body['artist_name']).one_or_none().id,
      venue_id = Venue.query.filter(Venue.name==body['venue_name']).one_or_none().id,
      start_time = body['start_time']
    )
    show.insert()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
