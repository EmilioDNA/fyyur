
#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import datetime
import sys 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db = SQLAlchemy(app)
migrate = Migrate(app, db)



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200), nullable=False)
    shows = db.relationship('Show', backref='venues', lazy=True, cascade='all, delete-orphan')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate




class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(120), nullable=False)
    shows = db.relationship('Show', backref='artists', lazy=True, cascade='all, delete-orphan')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime(), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

  @property
  def display_show(self):
    artist = Artist.query.filter(Artist.id==self.artist_id).one()
    venue = Venue.query.filter(Venue.id==self.venue_id).one()
    return {
      'venue_id': self.venue_id,
      'venue_name': venue.name,
      'artist_id': self.artist_id,
      'artist_name' : artist.name,
      'artist_image_link' : artist.image_link,
      'start_time': convert_datetime_string(self.start_time)}
  
  @property
  def display_show_venue(self):
    artist = Artist.query.filter(Artist.id==self.artist_id).one()
    return {
      'artist_id': self.artist_id,
      'artist_name' : artist.name,
      'artist_image_link' : artist.image_link,
      'start_time': convert_datetime_string(self.start_time)}

  @property
  def display_show_artist(self):
    venue = Venue.query.filter(Venue.id==self.venue_id).one()
    return {
      'venue_id': self.venue_id,
      'venue_name' : venue.name,
      'venue_image_link' : venue.image_link,
      'start_time':  convert_datetime_string(self.start_time)}
    



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def convert_string_datetime(datetime_str):
  return datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

def convert_datetime_string(datetime):
  return datetime.strftime( "%Y-%m-%d %H:%M:%S")
  

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
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  uniquecitiesanstate = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [dict(city=unique.city, 
                state=unique.state, 
                venues=[dict(id=v.id, 
                              name=v.name, 
                              num_upcoming_shows=Show.query.filter(Show.start_time > datetime.datetime.now(),
                                                                  Show.venue_id == v.id).count()
                              ) for v in Venue.query.filter(Venue.city == unique.city, 
                                          Venue.state == unique.state).all()]
                                          ) for unique in uniquecitiesanstate]
  
  return render_template('pages/venues.html', areas=data)


#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  qry = Venue.query.filter(Venue.name.like('%' + search_term + '%'))
  count = qry.count()
  venues = qry.all()
  list_venues = [dict(id=venue.id, 
                      name=venue.name, 
                      num_upcoming_shows= Show.query.filter(Show.venue_id ==venue.id).count() ) 
                      for venue in venues]
  response={
    "count": count,
    "data": list_venues
    
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


#  Venue with ID
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_object = Venue.query.get(venue_id)
  past_shows =  [show.display_show_venue for show in  Show.query.filter(datetime.datetime.now() > Show.start_time,
                                                                        Show.venue_id == venue_object.id)]
  upcoming_shows = [show.display_show_venue for show in  Show.query.filter(Show.start_time > datetime.datetime.now(),
                                                                           Show.venue_id == venue_object.id)]
  past_shows_count = Show.query.filter(datetime.datetime.now() > Show.start_time,
                                      Show.venue_id == venue_object.id).count()
  upcoming_shows_count = Show.query.filter(Show.start_time > datetime.datetime.now(),
                                          Show.venue_id == venue_object.id).count()

  data={
    "id": venue_object.id,
    "name": venue_object.name,
    "genres": venue_object.genres.split(", "),
    "address": venue_object.address,
    "city": venue_object.city,
    "state": venue_object.state,
    "phone": venue_object.phone,
    "website": venue_object.website,
    "facebook_link": venue_object.facebook_link,
    "seeking_talent": venue_object.seeking_talent,
    "seeking_description": venue_object.seeking_description,
    "image_link": venue_object.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

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
  error = False
  try:
    form_venue = request.form 
    genre_string = ', '.join([str(genre) for genre in form_venue.getlist('genres')])
    new_venue = Venue(name=form_venue['name'],
    city=form_venue['city'],
    state=form_venue['state'],
    address=form_venue['address'],
    phone=form_venue['phone'],
    genres=genre_string,
    facebook_link=form_venue['facebook_link'],
    image_link=form_venue['image_link'],
    website=form_venue['website'],
    seeking_talent=bool(form_venue['seeking_talent']),
    seeking_description=form_venue['seeking_description'])
    db.session.add(new_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # TODO: modify data to be the data object returned from db insertion
  if error:
    flash('An error ocurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_object = Venue.query.get(venue_id)
  venue={
    "id": venue_object.id,
    "name": venue_object.name,
    "genres": venue_object.genres.split(", "),
    "address": venue_object.address,
    "city": venue_object.city,
    "state": venue_object.state,
    "phone": venue_object.phone,
    "website": venue_object.website,
    "facebook_link": venue_object.facebook_link,
    "seeking_talent": venue_object.seeking_talent,
    "seeking_description": venue_object.seeking_description,
    "image_link": venue_object.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)


#  Edit Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    form_venue = request.form 
    genre_string = ', '.join([str(genre) for genre in form_venue.getlist('genres')])
    venue = Venue.query.get(venue_id)
    venue.name = form_venue['name']
    venue.city = form_venue['city']
    venue.state = form_venue['state']
    venue.address = form_venue['address']
    venue.phone = form_venue['phone']
    venue.genres = genre_string
    venue.facebook_link = form_venue['facebook_link']
    venue.image_link = form_venue['image_link']
    venue.website = form_venue['website']
    venue.seeking_talent = bool(form_venue['seeking_talent'])
    venue.seeking_description = form_venue['seeking_description']
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True 
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit() 
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error ocurred. the Venue could not be deleted.')
  else:
    # on successful db insert, flash success
    flash('The Venue was successfully deleted!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data_tuples = db.session.query(Artist.id, Artist.name).all()
  data = []
  for id, name in data_tuples:
    data.append(dict(id=id, name=name))

  
  return render_template('pages/artists.html', artists=data)


#  Search Artist
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  qry = Artist.query.filter(Artist.name.like('%' + search_term + '%'))
  count = qry.count()
  artists = qry.all()
  list_artists = [dict(id=artist.id, name=artist.name, num_upcoming_shows= Show.query.filter(Show.artist_id ==artist.id).count() ) for artist in artists]
  print(artists)
  print(count)
  print(list_artists)
  
  response={
    "count": count,
    "data": list_artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#  Artist with ID
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist_object = Artist.query.get(artist_id)
  past_shows =  [show.display_show_artist for show in  Show.query.filter(datetime.datetime.now() > Show.start_time,
                                                                        Show.artist_id == artist_object.id)]
  upcoming_shows = [show.display_show_artist for show in  Show.query.filter(Show.start_time > datetime.datetime.now() ,
                                                                        Show.artist_id == artist_object.id)]
  past_shows_count = Show.query.filter(datetime.datetime.now() > Show.start_time,
                                      Show.artist_id == artist_object.id).count()
  upcoming_shows_count = Show.query.filter(Show.start_time > datetime.datetime.now(),
                                          Show.artist_id == artist_object.id).count()

  data={
    "id": artist_object.id,
    "name": artist_object.name,
    "genres": artist_object.genres.split(", "),
    "city": artist_object.city,
    "state": artist_object.state,
    "phone": artist_object.phone,
    "website": artist_object.website,
    "facebook_link": artist_object.facebook_link,
    "seeking_venue": artist_object.seeking_venue,
    "seeking_description": artist_object.seeking_description,
    "image_link": artist_object.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_object = Artist.query.get(artist_id)
  artist={
    "id": artist_object.id,
    "name": artist_object.name,
    "genres": artist_object.genres.split(", "),
    "city": artist_object.city,
    "state": artist_object.state,
    "phone": artist_object.phone,
    "website": artist_object.website,
    "facebook_link": artist_object.facebook_link,
    "seeking_venue": artist_object.seeking_venue,
    "seeking_description": artist_object.seeking_description,
    "image_link": artist_object.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    form_artist = request.form 
    genre_string = ', '.join([str(genre) for genre in form_artist.getlist('genres')])
    artist = Artist.query.get(artist_id)
    artist.name = form_artist['name']
    artist.city = form_artist['city']
    artist.state = form_artist['state']
    artist.phone = form_artist['phone']
    artist.genres = genre_string
    artist.facebook_link = form_artist['facebook_link']
    artist.image_link = form_artist['image_link']
    artist.website = form_artist['website']
    artist.seeking_venue = bool(form_artist['seeking_venue'])
    artist.seeking_description = form_artist['seeking_description']
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True 
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))



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
  error = False
  try:
    form_artist = request.form 
    genre_string = ', '.join([str(genre) for genre in form_artist.getlist('genres')])
    new_artist = Artist(name=form_artist['name'],
    city=form_artist['city'],
    state=form_artist['state'],
    phone=form_artist['phone'],
    genres=genre_string,
    facebook_link=form_artist['facebook_link'],
    image_link=form_artist['image_link'],
    website=form_artist['website'],
    seeking_venue=bool(form_artist['seeking_venue']),
    seeking_description=form_artist['seeking_description'])
    db.session.add(new_artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True 
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.order_by('id').all()
  data = [show.display_show for show in shows]
  print(datetime.datetime.now())
  return render_template('pages/shows.html', shows=data)


#  Create Show
#  ----------------------------------------------------------------
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    form_show = request.form
    new_show = Show(artist_id=form_show['artist_id'],
    venue_id=form_show['venue_id'],
    start_time=form_show['start_time'])
    db.session.add(new_show)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True 
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
