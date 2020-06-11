import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    Processes song json files given a filepath and inserts in songs and artists tables

    :param cur: cursor to database connection
    :param filepath: path to a song json file
    :returns: nothing
    :raises Error: raises an exception if unable to execute query
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = list(df[["song_id", "title", "artist_id", "year", "duration"]].values[0])
    try:
        cur.execute(song_table_insert, song_data)
    except psycopg2.Error as e:
        print("Error: Unable to insert record in songs table")
        print(e)

    # insert artist record
    artist_data = list(df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]].values[0])
    try:
        cur.execute(artist_table_insert, artist_data)
    except psycopg2.Error as e:
        print("Error: Unable to insert record in artists table")
        print(e)

def process_log_file(cur, filepath):
    """
    Processes log json files given a filepath and inserts in time, users and songplays tables

    :param cur: cursor to database connection
    :param filepath: path to a log json file
    :returns: nothing
    :raises Error: raises an exception if unable to execute query
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page']=='NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')
    
    # insert time data records
    #timestamp, hour, day, week of year, month, year, and weekday
    hour = t.dt.hour
    day = t.dt.day
    weekofyear = t.dt.weekofyear
    month = t.dt.month
    year = t.dt.year
    weekday = t.dt.weekday

    time_data = [df['ts'], hour, day, weekofyear, month, year, weekday]
    column_labels = ['timestamp', 'hour', 'day', 'week of year', 'month', 'year', 'weekday']
    time_df = pd.DataFrame.from_dict(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        try:
            cur.execute(time_table_insert, list(row))
        except psycopg2.Error as e:
            print("Error: Unable to insert record in time table in row number : {}".format(i))
            print(e)

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        try:
            cur.execute(user_table_insert, row)
        except psycopg2.Error as e:
            print("Error: Unable to insert record in users table in row number : {}".format(i))
            print(e)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        try:
            cur.execute(song_select, (row.song, row.artist, row.length))
        except psycopg2.Error as e:
            print("Error: Unable to execute song_select query to join songs and artists table in row number : {}".format(index))
            print(e)
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        #timestamp, user ID, level, song ID, artist ID, session ID, location, and user agent
        songplay_data = (row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        try:
            cur.execute(songplay_table_insert, songplay_data)
        except psycopg2.Error as e:
            print("Error: Unable to insert record in songplays table in row number : {}".format(i))
            print(e)


def process_data(cur, conn, filepath, func):
    """
    Generates the json files list and calls helper function to insert records in fact and dim tables

    :param cur: cursor to database connection
    :param conn: database connection
    :param filepath: path to the root folder for json files
    :param func: function to be applied on the json file
    :returns: nothing
    :raises Error: raises no exception
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        # use the func to insert data from these files to database's fact and dim tables
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
    Sets up database connection & inserts records in fact and dim tables using song and log data files

    :raises Error: raises an exception if unable to execute query
    """
    # Create a connection to database
    try:
        conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    except psycopg2.Error as e:
        print("Error: Unable to make connection to Postgres Database {}".format("sparkifydb"))
        print(e)
    
    # Get cursor
    try:
        cur = conn.cursor()
    except psycopg2.Error as e:
        print("Error: Unable to get cursor to the Database")
        print(e)

    # set the autocommit to true to avoid conn.commit() after each command
    conn.set_session(autocommit=True)

    # use the process_data function to get all log and song data files contents inserted in tables
    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    # Close the connection to the database
    conn.close()


if __name__ == "__main__":
    main()