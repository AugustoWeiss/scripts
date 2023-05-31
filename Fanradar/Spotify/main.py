import sys
import uuid
import random
import string
import hashlib
import datetime
import mysql.connector
from spotify import Spotify
from const import HOST, USER, PASSWORD, DATABASE

def connect_db():
    return mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )

def create_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    hashed_password = hashlib.sha256(password.encode())
    return hashed_password.hexdigest()

def create_user(db, artist_info):
    query = """
        INSERT INTO users (uuid, username, email, country_id, state_id, password, owner, permission_level, is_talent, is_bot, is_from_spotify, created_at)
        SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        WHERE NOT EXISTS (
            SELECT 1 FROM spotify_info WHERE spotify_id=%s
        )
    """
    new_uuid = uuid.uuid1().hex
    username = artist_info['name'].lower().replace(" ", ".")
    email = "%s@fanradar.com" % username
    password = create_random_password()
    create_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    values = (
        new_uuid, username, email, 11, 4880, password, 0, 200, 1, 1, 1, create_date, artist_info['id']
    )
    cr = db.cursor()
    cr.execute(query, values)
    db.commit()
    user_id = cr.lastrowid
    cr.close()
    return user_id

def load_spotify_info(db, artist_info, user_id):
    query = """
        INSERT INTO spotify_info (user_id, spotify_id, url, image, followers, popularity, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        user_id, artist_info['id'], "", artist_info['images']['url'], artist_info['followers']['total'], artist_info['popularity'], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    cr = db.cursor()
    cr.execute(query, values)
    db.commit()
    cr.close()
    return

def get_related_artists(spotify, artist):
    related_artists = spotify.get_related_artists(artist)
    if related_artists:
        related_artists_ids = [artist["id"] for artist in related_artists["artists"]]
        return related_artists_ids
    else:
        return False

def load_from_spotify(db, spotify, artist_id, RECURSION):
    if RECURSION > MAX_RECURSION:
        return
    artist_info = spotify.get_artist_by_id(artist_id)
    user_id = create_user(db, artist_info)
    if user_id:
        load_spotify_info(db, artist_info, user_id)
    related_artists_ids = get_related_artists(spotify, artist)
    for artist in related_artists_ids:
        load_from_spotify(db, spotify, artist, RECURSION+1)


def main():
    if len(sys.argv) == 1:
        print("Error: Introducir ids de artistas espaciados")
        print("Ejemplo: Qwe123rty asD456fgh")
        return

    artist_ids = sys.argv[1:]
    spotify = Spotify()
    db = connect_db()

    for artist_id in artist_ids:
        RECURSION = 0
        load_from_spotify(db, spotify, artist_id, RECURSION+1)
    db.close()


if __name__ == '__main__':
    MAX_RECURSION = 1
    main()
