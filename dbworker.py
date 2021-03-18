#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3 as sql


class DBWorker:

	def __init__(self, database):
		"""

		"""
		self.connection = sql.connect(database)
		self.cursor = self.connection.cursor()

	def add_user(self, user_id, status=1):
		with self.connection:
			return self.cursor.execute("INSERT INTO 'user_state' ('user_id', 'status') VALUES (?, ?)", (user_id, status))

	def user_exist(self, user_id):
		with self.connection:
			rez = self.cursor.execute("SELECT * FROM 'user_state' WHERE `user_id` = ?", (user_id,)).fetchall()
			return bool(len(rez))
