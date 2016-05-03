import unittest
import os
import shutil
import json
try: from urllib.parse import urlparse
except ImportError: from urlparse import urlparse # Py2 compatibility
from io import StringIO

import sys; print(list(sys.modules.keys()))
# Configure our app to use the testing databse
os.environ["CONFIG_PATH"] = "tuneful.config.TestingConfig"

from tuneful import app
from tuneful import models
from tuneful.utils import upload_path
from tuneful.database import Base, engine, session

class TestAPI(unittest.TestCase):
    """ Tests for the tuneful API """

    def setUp(self):
        """ Test setup """
        self.client = app.test_client()

        # Set up the tables in the database
        Base.metadata.create_all(engine)

        # Create folder for test uploads
        os.mkdir(upload_path())

    def tearDown(self):
        """ Test teardown """
        session.close()
        # Remove the tables and their data from the database
        Base.metadata.drop_all(engine)

        # Delete test upload folder
        shutil.rmtree(upload_path())
    
    def test_get_uploaded_file(self):
        path =  upload_path("test.txt")
        with open(path, "wb") as f:
            f.write(b"File contents")

        response = self.client.get("/uploads/test.txt")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/plain")
        self.assertEqual(response.data, b"File contents")

    def test_get_songs(self):
        # test getting all songs in db
        
        # populate db
        file_A = models.File(name='file_A.mp3')
        song_A = models.Song(file=file_A)
        file_B = models.File(name='file_B.mp3')
        song_B = models.Song(file=file_B)
        session.add_all([file_A, file_B, song_A, song_B])
        session.commit()

        response = self.client.get('/api/songs',
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')

        data = json.loads(response.data.decode('ascii'))
        self.assertEqual(len(data), 2)
        
        # store JSON structured data for each test
        response_song_A, response_song_B = data
        # assert tests for first song
        self.assertEqual(response_song_A['id'], song_A.id)
        self.assertEqual(response_song_A['file']['id'], song_A.file.id)
        self.assertEqual(response_song_A['file']['name'], song_A.file.name)
        # assert tests for second song
        self.assertEqual(response_song_B['id'], song_B.id)
        self.assertEqual(response_song_B['file']['id'], song_B.file.id)
        self.assertEqual(response_song_B['file']['name'], song_B.file.name)

    def test_post_song(self):
        # test posting song into db
        
        file_A = models.File(name='file_A.mp3')
        session.add(file_A)
        session.commit()

        data = {
            "file": { "id": file_A.id }
        }

        response = self.client.post("/api/songs",
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")]
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["id"], 1)
        self.assertEqual(data["file"]["name"], "file_A.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        song = songs[0]
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file.id, 1)
        self.assertEqual(song.file.name, "file_A.mp3")

    def test_get_song(self):
        # test for getting one song
    
        # populate db
        file_A = models.File(name='file_A.mp3')
        song_A = models.Song(file=file_A)
        file_B = models.File(name='file_B.mp3')
        song_B = models.Song(file=file_B)
        session.add_all([file_A, file_B, song_A, song_B])
        session.commit()

        response = self.client.get(
            '/api/songs/{}'.format(song_B.id),
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/json')

        song = json.loads(response.data.decode('ascii'))
        
        self.assertEqual(song['id'], song_B.id)
        self.assertEqual(song['file']['id'], song_B.file.id)
        self.assertEqual(song['file']['name'], song_B.file.name)

    def test_edit_song(self):
        # test editing a song in db

        # populate db
        file_A = models.File(name='file_A.mp3')
        song_A = models.Song(file=file_A)
        file_B = models.File(name='file_B.mp3')
        song_B = models.Song(file=file_B)
        session.add_all([file_A, file_B, song_A, song_B])
        session.commit()

        data = { "file": { "id": file_A.id } }

        response = self.client.put(
            "/api/songs/{}".format(song_A.id),
            data=json.dumps(data),
            content_type="application/json",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["id"], 1)
        self.assertEqual(data["file"]["name"], "file_A.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 2)

        song = songs[0]
        self.assertEqual(song.id, 1)
        self.assertEqual(song.file.id, 1)
        self.assertEqual(song.file.name, "file_A.mp3")

    def test_delete_song(self):
        # test deleting a song
        
        # populate db
        file_A = models.File(name='file_A.mp3')
        song_A = models.Song(file=file_A)
        file_B = models.File(name='file_B.mp3')
        song_B = models.Song(file=file_B)
        session.add_all([file_A, file_B, song_A, song_B])
        session.commit()

        response = self.client.delete(
            "/api/songs/{}".format(song_A.id),
            content_type="application/json",
            headers=[("Accept", "application/json")])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/json")

        data = json.loads(response.data.decode("ascii"))
        self.assertEqual(data["id"], 1)
        self.assertEqual(data["file"]["id"], 1)
        self.assertEqual(data["file"]["name"], "file_A.mp3")

        songs = session.query(models.Song).all()
        self.assertEqual(len(songs), 1)

        files = session.query(models.File).all()
        self.assertEqual(len(files), 1)
        file = files[0]
        self.assertEqual(file.id, 2)
        self.assertEqual(file.name, 'file_B.mp3')