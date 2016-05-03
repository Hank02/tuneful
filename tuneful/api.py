import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

# JSON Schema describing the structure of a song
song_schema = {
    "definitions": { "file": { "type": "object", "properties": { "id": {"type": "number"} } } },
    "properties": { "file": { "$ref": "#/definitions/file" } },
    "required": ["file"]
}

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

@app.route('/api/songs', methods=['GET'])
@decorators.accept("application/json")
def get_songs():
    # get a list of all songs in db
    song_list = session.query(models.Song)
    song_list = song_list.order_by(models.Song.id)
    
    # convert song list into JSON and return
    result = json.dumps([song.as_dictionary() for song in song_list])
    return Response(result, 200, mimetype='application/json')

@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def post_song():
    # add song to db
    data = request.json

    # Check that the JSON supplied is valid, if not you return a 422 Unprocessable Entity
    try:
        validate(data, song_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")
    
    # make sure song exists
    file_ = session.query(models.File).get(data['file']['id'])
    if not file_:
        message = "Could not find file with id {}".format(data['file']['id'])
        error = json.dumps({'message': error.message})
        return Response(error, 404, mimetype='application/json')

    # add song to db
    song = models.Song(file_id=data["file"]["id"])
    session.add(song)
    session.commit()

    # Return a 201 Created, containing the song as JSON and with the
    # location header set to the location of the song
    data = json.dumps(song.as_dictionary())
    return Response(data, 201, mimetype="application/json")

@app.route('/api/songs/<int:id>', methods=['GET'])
@decorators.accept("application/json")
def get_song(id):
    # get one song from db
    song = session.query(models.Song).get(id)
    
    # make sure song is in db
    if song:
        data = json.dumps(song.as_dictionary())
        return Response(data, 200, mimetype='application/json')
    else:
        message = 'Could not find song with id {}'.format(id)
        data = json.dumps({'message': message})
        return Response(data, 404, mimetype='application/json')








# @app.route('/api/songs/<int:id>', methods=['PUT'])
# @decorators.accept("application/json")
# @decorators.require("application/json")
# def put_song(id):
#     song = session.query(models.Song).get(id)

#     if not song:
#         message = 'Could not find song with id {}'.format(id)
#         data = json.dumps({'message': message})
#         return Response(data, 404, mimetype='application/json')

#     data = request.json
#     # Check that the JSON supplied is valid
#     # If not you return a 422 Unprocessable Entity
#     try:
#         jsonschema.validate(data, song_schema)
#     except jsonschema.ValidationError as error:
#         error = json.dumps({"message": error.message})
#         return Response(error, 422, mimetype="application/json")

#     file_ = session.query(models.File).get(data['file']['id'])
#     if not file_:
#         message = 'Could not find file with id {}'.format(data['file']['id'])
#         error = json.dumps({'message': message})
#         return Response(error, 404, mimetype='application/json')

#     # Add the song to the database
#     song.file_ = file_
#     session.add(song)
#     session.commit()

#     data = json.dumps(song.as_dict())
#     return Response(data, 200, mimetype="application/json")

# @app.route('/api/songs/<int:id>', methods=['DELETE'])
# @decorators.accept("application/json")
# @decorators.require("application/json")
# def delete_song(id):
#     song = session.query(models.Song).get(id)

#     if not song:
#         message = 'Could not find song with id {}'.format(id)
#         data = json.dumps({'message': message})
#         return Response(data, 404, mimetype='application/json')

#     session.delete(song)
#     session.commit()

#     data = json.dumps(song.as_dict())
#     return Response(data, 200, mimetype="application/json")