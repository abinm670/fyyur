#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from numpy.ma.core import append
from forms import * 

# ---------
from sqlalchemy import func
from sqlalchemy import tuple_
import pandas as pd
import operator
import itertools
import pprint
from collections import defaultdict





#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)



# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website=db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    seeking_talent=db.Column(db.Boolean, default=False, server_default="false")
    seeking_description=db.Column(db.String(500))
    show_ven = db.relationship('Show',  backref='ven', cascade="all, delete" , lazy=True )
    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.genres}{self.city} {self.address}{self.phone}{self.image_link}{self.facebook_link}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    seeking_description=db.Column(db.String(500))
    seeking_venue=db.Column(db.Boolean, default=False, server_default="false")
    facebook_link = db.Column(db.String(500))
    website=db.Column(db.String(500))
    show_art = db.relationship('Show',  backref='art', cascade="all, delete" , lazy=True  )
def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.city} {self.state}{self.phone} {self.genres} {self.image_link} {self.facebook_link} >'
def sendId():
      return db.session.query(Artist.id).all()
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
        __tablename__ = 'shows'
        show_id=db.Column(db.Integer, primary_key=True)
        artist_id=db.Column(db.Integer, db.ForeignKey('artists.id', ondelete="CASCADE"))
        venue_id=db.Column(db.Integer, db.ForeignKey('venues.id', ondelete="CASCADE")) 
        start_time=db.Column(db.DateTime, nullable=False)
        
        # no_overlapped=db.UniqueConstraint('artist_id', 'venue_id', 'date', name ="no_overL")
        
def __repr__(self):
      return f'<Show {self.start_time} {self.venue_id} {self.artist_id} >'
    # Ref ===> https://www.programcreek.com/python/example/78978/sqlalchemy.Date
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


#----------------------------------------------
@app.route('/venues')
def venues():

    num_upcoming_shows=0
 
      
    data=[]
    venue_date=[]
    art=Venue.query.all()
    for i in art:
          data.append({
            "city":i.city,
            "state":i.state,
            "venues":[{
              "id":i.id, 
              "name":i.name}]}) 

  
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
 
  search_term = request.form.get('search_term', '')
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  
  response2=[]
  for i in result:
    response2.append({
      "id":i.id,
      "name":i.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == i.id).filter(Show.start_time >datetime.now()).all())
    })

  response1={
      "count":len(result),
      "data":response2
    }
  print(response1)

  return render_template('pages/search_venues.html', results=response1, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  cuurent_date = datetime.now()
  ven=db.session.query(Venue.id, Venue.name, Venue.genres, Venue.address , Venue.city, Venue.state, Venue.phone,\
    Venue.facebook_link, Venue.show_ven,Venue.seeking_description, Venue.image_link,\
      Venue.seeking_talent, Artist.id,Artist.name, Artist.image_link, Show.start_time).\
      filter(Venue.id==venue_id).\
      join(Show, Show.venue_id == Venue.id).join(Artist, Show.venue_id == Artist.id).distinct()
 
  ven= (list(db.session.execute(ven)))
  ven_all=Venue.query.get(venue_id)
  past_shows=[]
  upcoming_shows=[]
  # print(ven.index())
  data1=[]

  for i in ven:
    
      shows ={
                    "artist_id":i[12],
                    "venue_name":i[1],
                    "artist_name":i[13],
                    "artist_image_link":i[14],
                    "start_time": str(i[15])}
      if datetime.strptime(shows['start_time'], "%Y-%m-%d %H:%M:%S") < datetime.now():
        past_shows.append(shows)
      else:
        upcoming_shows.append(shows)
      
      data1={
        "name": ven_all.name,
        "genres":ven_all.genres, 
        "address":ven_all.address, 
        "city":ven_all.city,
        "phone":ven_all.phone,
        "website":ven_all.website,
        "facebook_link":ven_all.facebook_link,
        "seeking_talent":ven_all.seeking_talent,
        "seeking_description":ven_all.seeking_description,
        "image_link":ven_all.image_link,
        "past_shows":past_shows,
        "past_shows_count":len(past_shows),
        "upcoming_shows_count":len(upcoming_shows)

      }

      print(data1)
  return render_template('pages/show_venue.html', venue=data1)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

 error=False

 try:
  new = Venue(
    name=request.form['name'],
    city=request.form['city'],
    state=request.form['state'],
    address=request.form['address'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    facebook_link=request.form['facebook_link'],
    seeking_talent= (True if 'seeking_talent' in request.form else False),
    seeking_description=request.form['seeking_description'],
    image_link=request.form['image_link'])

  db.session.add(new)
  db.session.commit()
  

 except:
   error=True
   flash('An error occurred. Venue ' + "test"+ ' could not be listed.')
   db.session.rollback()
   print(sys.exc_info())

 finally:
    db.session.close()
    if not error:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
 return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error=False 
  venue=Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
  except:
    error=True
    flash("couldnt delete")
    db.session.rollback()
    print(sys.exc_info)
  finally:
    db.session.close()
  if not error:
    flash("venue has been deleted" + venue.name)

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  art=Artist.query.all()
  data=[]
  for i in art:\
    data.append({\
      "id":i.id,
      "name":i.name
      })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term= request.form.get('search_term', '')
  response1=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
    

  data =[]
  for i in response1:
    
    data.append({
      "id":i.id,
      "name":i.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == i.id).filter(Show.start_time > datetime.now()).all())
      })
    
          
    response={
      "count":len(response1),
      "data":data}
    
 
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist_data=Artist.query.get(artist_id)
  # data=Artist.query.filter_by(artist_id).all()
  venue_date=db.session.query(Venue).join(Show).with_entities(Venue.id, Venue.name, Venue.image_link, Show.start_time).\
  filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()
  venue_date_new=db.session.query(Venue).join(Show).with_entities(Venue.id, Venue.name, Venue.image_link, Show.start_time).\
  filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

  past_shows = []
  upcoming_shows=[]

  for i in venue_date:
    past_shows.append({
        "venue_id": i[0] ,
        "venue_name": i[1],
        "venue_image_link": i[2],
        "start_time":str(i[3]), 
        })
  
 

  for i in venue_date_new:
      upcoming_shows.append({
          "venue_id": i[0] ,
          "venue_name": i[1],
          "venue_image_link": i[2],
          "start_time":str(i[3])
          })
    
  

  data1={
  "id": artist_data.id,
  "name": artist_data.name,
  "genres": artist_data.genres,
  "city": artist_data.city,
  "state": artist_data.state,
  "phone": artist_data.phone,
  "website": artist_data.website,
  "facebook_link": artist_data.facebook_link,
  "seeking_venue": artist_data.seeking_venue,
  "seeking_description": artist_data.seeking_description,
  "image_link": artist_data.image_link,
  "past_shows": past_shows,
  "upcoming_shows": upcoming_shows ,
  "past_shows_count": len(venue_date),
  "upcoming_shows_count": len(venue_date_new),
  }
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)

  
  artist1={
    "id": artist.id,
    "name":artist.name,
    "genres":artist.genres,
    "city":artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link, 
    "website": artist.website,
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist1)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  art=Artist.query.get(artist_id)

  try:
    art.name=request.form['name']
    art.genres=request.form.getlist('genres')
    art.state=request.form['state']
    art.city=request.form['city']
    art.phone=request.form['phone']
    art.facebook_link=request.form['facebook_link']
    art.seeking_venue=True if 'seeking_venue' in request.form else False
    art.seeking_description=request.form['seeking_description']
    art.image_link=request.form['image_link']
    art.website=request.form['website']

    db.session.commit()

  except:
    flash("wrong")
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    flash("good job")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  data=Venue.query.get(venue_id)

  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  error=False
  data=Venue.query.get(venue_id)

  try:
    data.name=request.form['name']
    data.city=request.form['city']
    data.state=request.form['state']
    data.address=request.form['address']
    data.phone=request.form['phone']
    data.genres=request.form.getlist('genres')
    data.facebook_link=request.form['facebook_link']
    data.seeking_talent=True if 'seeking_talent' in request.form else False
    data.seeking_description=request.form['seeking_description']
    data.image_link=request.form['image_link']
    data.website=request.form['website']
    db.session.commit()

  except:
    error=True
    flash('An error occurred. Venue ' + request.form['name']+ ' could not be edit.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash("Venue  " + request.form['name'] + "  has been edited")



    seeking_talent= (True if 'seeking_talent' in request.form else False),
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
  
  try:
    
    new=Artist(
    name=request.form['name'],
    city=request.form['city'],
    state= request.form['state'],
    phone=request.form['phone'],
    genres=request.form.getlist('genres'),
    facebook_link=request.form['facebook_link'])
    db.session.add(new)
    db.session.commit()
    # print(new)
  except :
    error=True
    flash('Artist ' + request.form['name'] + ' was not working listed!' )
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # if not error:
  #        flash('Artist ' + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/shows')
def shows():
   
  shows_info= db.session.query(\
     Venue.id, Venue.name , Artist.id , Artist.name , Artist.image_link, Show.start_time).join(\
      Show, Show.artist_id==Artist.id).join(\
        Venue, Show.artist_id == Venue.id).order_by(Artist.id).subquery()
 
  shows_info=list(db.session.execute(shows_info))

  
  shows_info=pd.DataFrame(shows_info, columns=['venue_id', 'venue_name', 'artist_id', 'artist_name', 'artist_image_link','start_time' ])
  pprint.pprint(shows_info)
  shows_info['start_time']=shows_info['start_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
  # print(shows_info.dtypes)
  shows_info=shows_info.T.to_dict().values()
  pprint.pprint(shows_info)
  shows_info=list(shows_info)
  pprint.pprint(shows_info)
  # print(shows_info[0])

  return render_template('pages/shows.html', shows=shows_info)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  
  
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error=False

  try:
    new=Show(
      artist_id=request.form['artist_id'], 
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time']
    )
    db.session.add(new)
    db.session.commit()

  except:
    error=True
    flash('Show' + request.form['venue_id'] + 'was not created')
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()
    flash('Show' + request.form['venue_id'] + 'crated')
  
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


'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
