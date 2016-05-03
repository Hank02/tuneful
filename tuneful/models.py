import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine

class Song(Base):
    # The Song model: This should have an integer id column,
    # and a column specifying a one-to-one relationship with a File.
    # The Song.as_dictionary method should produce a dictionary which looks something like this:
    # {"id": 1,"file": {"id": 7,"name": "Shady_Grove.mp3"}}
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)
    file = relationship("File", uselist=False, backref="song")
    file_id = Column(Integer, ForeignKey('files.id'))
     
    def as_dictionary(self):
        song = { 
            "id": self.id,
            "file": self.file.as_dictionary() }
        return song
        

class File(Base):
    #The File model: This should have an integer id column, 
    # a string column for the filename, and the backref from 
    # the one-to-one relationship with the Song.
    # The File.as_dictionary method should just return the file element
    # of the song dictionary (i.e. {"id": 7, "name": "Shady_Grove.mp3"}).
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))

    def as_dictionary(self):
        file = { 
            "id": self.id, 
            "name": self.name, 
            "path": url_for("uploaded_file", filename=self.name) }
        return file