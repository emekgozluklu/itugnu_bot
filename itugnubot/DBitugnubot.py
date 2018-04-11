import sqlite3

class DB:
	def __init__(self, dbname="itugnu.sqlite"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def setup(self):
		tblstmt = "CREATE TABLE IF NOT EXISTS events (Etkinlik_Adi text, Tarih text, Gecmis integer)"
		usrstmt = "CREATE TABLE IF NOT EXISTS users (user_id integer, username text)"
		itemidx = "CREATE INDEX IF NOT EXISTS eventIndex ON events (Etkinlik_Adi ASC)"
		self.conn.execute(tblstmt)
		self.conn.execute(usrstmt)
		self.conn.execute(itemidx)
		self.conn.commit()

	def add_event(self, event_name, tarih):
		stmt = "INSERT INTO events (Etkinlik_Adi, Tarih, Gecmis) VALUES (?, ?, ?)"
		args = (event_name, tarih, 0)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def delete_event(self, event_name):
		stmt = "DELETE FROM events WHERE Etkinlik_Adi = (?)"
		args = (event_name)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def get_events(self):
		stmt = "SELECT Etkinlik_Adi, Tarih FROM events WHERE Gecmis = (?)"
		args = (0, )
		events = self.conn.execute(stmt, args)
		son = []
		for event in events:
			son.append(event)
		return son

	def add_user(self, user_id, username):
		stmt = "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)"
		args = (user_id, username)
		self.conn.execute(stmt, args)
		self.conn.commit()


	def get_username(self, user_id):
		stmt = "SELECT username FROM users WHERE user_id=(?)"
		args = (user_id,)
		username = self.conn.execute(stmt, args)
		return username

	def get_user_id(self, username):
		stmt = "SELECT user_id FROM users WHERE username=(?)"
		args = (username,)
		user_ids = self.conn.execute(stmt, args)
		for user_id in user_ids:
			return user_id


	def delete_user(self, user_id):
		stmt = "DELETE FROM users WHERE user_id=(?)"
		args = (user_id, )
		self.conn.execute(stmt, args)
		self.conn.commit()
