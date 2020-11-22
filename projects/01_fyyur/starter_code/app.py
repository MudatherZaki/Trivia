#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
  Flask,
  render_template,
  request, 
  Response, 
  flash, 
  redirect, 
  url_for)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from sqlalchemy import func
from models import app, db, Show, Artist, Venue

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)


#----------------------------------------------------------------------------#
# Models. DONE
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(value, format, locale='en')

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
  data = []
  for venue_city in Venue.query.distinct(Venue.city).all():
        venues = Venue.query.filter_by(city=venue_city.city).all()
        venues_list = []
        for venue in venues:
              upcoming_shows = list(filter(lambda d: d.start_date > date.today(), venue.shows))
              venue_record = {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows)
              }
              venues_list.append(venue_record)
        record = {
          "city" : venue_city.city,
          "state": venues[0].state,
          "venues": venues_list
        }
        data.append(record)
        
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '').casefold()
  venues = Venue.query.filter(func.lower(Venue.name).like('%' + search_term + '%')).all()
  data = []
  for venue in venues:
        upcoming_shows_query = list(filter(lambda d: d.start_date >= date.today(), venue.shows))
        record = {
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(upcoming_shows_query),
        }
        data.append(record)
  response={
    "count": len(data),
    "data": data
    }
  
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  # past_shows_query = list(filter(lambda d: d.start_date < date.today(), venue.shows))
  past_shows_query = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_date < datetime.now()
    ).all()
  # upcoming_shows_query = list(filter(lambda d: d.start_date >= date.today(), venue.shows))
  upcoming_shows_query = upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_date > datetime.now()
    ).all()
  past_shows = []
  upcoming_shows = []
  for artist, show in past_shows_query:
        record = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_date
        }
        past_shows.append(record)
  for artist, show in upcoming_shows_query:
        record = {
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_date
        }
        upcoming_shows.append(record)
  
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  form = VenueForm(request.form)
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occured. Venue ' + req['name'] + ' could not be listed!')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except :
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
        record ={
          "id": artist.id,
          "name": artist.name
        }
        data.append(record)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '').casefold()
  artists = Artist.query.filter(func.lower(Artist.name).like('%' + search_term + '%')).all()
  data = []
  for artist in artists:
        upcoming_shows_query = list(filter(lambda d: d.start_date >= date.today(), artist.shows))
        record = {
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(upcoming_shows_query),
        }
        data.append(record)
  response={
    "count": len(data),
    "data": data
    }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  past_shows_query = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_date < datetime.now()
    ).all()
  upcoming_shows_query = db.session.query(Venue, Show).join(Show).join(Artist).filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_date > datetime.now()
    ).all()
  past_shows = []
  upcoming_shows = []
  for venue, show in past_shows_query:
        record = {
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_date
        }
        past_shows.append(record)
  for venue, show in upcoming_shows_query:
        record = {
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.start_date
        }
        upcoming_shows.append(record)
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": [] if artist.genres is None else artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  form.city.data = artist.city
  form.name.data = artist.name
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = [] if artist.genres is None else artist.genres.split(',')
  form.facebook_link.data = artist.facebook_link
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": [] if artist.genres is None else artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  req = request.form

  artist.city = req['city']
  artist.name = req['name']
  artist.state = req['state']
  artist.phone = req['phone']
  artist.genres = req['genres']
  artist.facebook_link = req['facebook_link']

  try:
    db.session.commit()
  except:
    db.serssion.rollback()
  finally:
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  form.city.data = venue.city
  form.name.data = venue.name
  form.address.data = venue.address
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = [] if venue.genres is None else venue.genres.split(',')
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = '' if venue.seeking_description is None else venue.seeking_description
  form.website_link.data = '' if venue.website_link is None else venue.website_link
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": [] if venue.genres is None else venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  req = request.form

  venue.city = req['city']
  venue.address = req['address']
  venue.name = req['name']
  venue.state = req['state']
  venue.phone = req['phone']
  venue.genres = req['genres']
  venue.facebook_link = req['facebook_link']

  try:
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValueError as e:
    print(e)
    flash('An error occurred. Artist ' + req['name'] + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
        record = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_date
        }
        data.append(record)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  req = request.form
  show = Show(
    start_date = datetime.strptime(req['start_time'],'%Y-%m-%d %H:%M:%S'),
    venue_id = int(req['venue_id']),
    artist_id = int(req['artist_id'])
  )

  try:
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  finally:
    db.session.close()
  flash('Show was successfully listed!')

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


