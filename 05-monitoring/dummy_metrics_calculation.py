import datetime
import time
import random
import logging 
import uuid
import psycopg2.sql
import pytz
import pandas as pd
import io
import psycopg2

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	value1 integer,
	value2 varchar,
	value3 float
)
"""
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "example"
DB_DATABASE = "test"

def prep_db():
	with psycopg2.connect(
		user=DB_USER,
		password=DB_PASS,
		host=DB_HOST,
		port=DB_PORT
	) as conn:
		conn.autocommit = True
		curr = conn.cursor()

		curr.execute("SELECT 1 FROM pg_database WHERE datname='test'")

		have_db = curr.fetchall()

	if len(have_db) == 0:
		logging.debug("Creating database called test...")
		conn = psycopg2.connect(
			user=DB_USER,
			password=DB_PASS,
			host=DB_HOST,
			port=DB_PORT
		)
		conn.autocommit = True
		curr = conn.cursor()
		curr.execute("create database test;")
		conn.close()
		# with psycopg2.connect(
		# 	user=DB_USER,
		# 	password=DB_PASS,
		# 	host=DB_HOST,
		# 	port=DB_PORT
		# ) as conn:
		# 	conn.autocommit = True
		# 	curr = conn.cursor()
		# 	curr.execute("create database test;")
			
	with psycopg2.connect(
			database=DB_DATABASE,
			user=DB_USER,
			password=DB_PASS,
			host=DB_HOST,
			port=DB_PORT
		) as conn:
			conn.autocommit = True
			curr = conn.cursor()
			curr.execute(create_table_statement)


def calculate_dummy_metrics_postgresql(curr):
	value1 = rand.randint(0, 1000)
	value2 = str(uuid.uuid4())
	value3 = rand.random()

	curr.execute(
		"insert into dummy_metrics(timestamp, value1, value2, value3) values (%s, %s, %s, %s)",
		(datetime.datetime.now(pytz.timezone('Europe/London')), value1, value2, value3)
	)

def main():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)

	with psycopg2.connect(
		database=DB_DATABASE,
		user=DB_USER,
		password=DB_PASS,
		host=DB_HOST,
		port=DB_PORT
	) as conn:
	# with psycopg2.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
		conn.autocommit = True
		for _ in range(0, 100):
			with conn.cursor() as curr:
				calculate_dummy_metrics_postgresql(curr)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	main()