# SparkifyDb   

#### Purpose
The ETL project is designed and implemented to help my company Sparkify to perform analysis on users' song play activity using our new music app.

#### Database schema design and ETL pipeline
Database design follows the STAR schema for tables. It has a Fact table : songplays and four Dimension tables: songs, artists, time and users.

**What** the user was listening to (songs)
**Which** artist was user listening to (artists)
**When** the user was listening to the songs (time)
**Who** was listening the songs (users)

**How** and Where the user was listening to the songs (songplays)


The data is ingested from two source folders _song_data_ and _log_data_ in form of json files using pandas library in Python. Data is further filtered, cleaned and recorded in the tables using Postgres SQL and Python (psycopg2) statements and commands. The tables are in their normal form to avoid any duplication and taking into consideration the efficiency of running the most frequent queries.

#### Example of some analysis query:
- How many paid users were there?
   ```sh
  %sql SELECT count(*) from users where level='paid';
   ```
- How many free users were there?
   ```sh
  %sql SELECT count(*) from users where level='free';
   ```
- Most frequently listened artists or songs?
   ```sh
  %sql SELECT song_id, COUNT(song_id) from songplays GROUP BY song_id ORDER BY COUNT(song_id) DESC LIMIT 1;
  %sql SELECT artist_id, COUNT(artist_id) from songplays GROUP BY artist_id ORDER BY COUNT(artist_id) DESC LIMIT 1;
   ```


#### How to use the product?
1. Run create_tables.py from terminal using ) to drop existing Sparkify database/tables and create new database/tables.
```sh
root@0cc7f703976a:/home/workspace# python create_tables.py
```
2. Run etl.py from terminal to read in json files from song_data and log_data and insert records in the tables.
```sh
root@0cc7f703976a:/home/workspace# python etl.py
```
3. Use test.ipynb provided to add and run analytical queries.   


### REMEMBER: Make sure to `close` connection to sparkifydb
Remember to close the connection to sparkify database after use since multiple connections to the same database are not allowed.