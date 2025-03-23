# This file is only for testing the file filter functionality
import os
import json
import numpy as np
from utils import *
from os.path import join

__all__ = ['query_database', 'insert_database', 'delete_database', 'db', 'Document']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Document:
	"""
	Document class to store the data
	The json_data must have the following fields:
	- id: unique identifier
	- vector: vector representation of the document
	"""
	def __init__(self, json_data):
		self.id = json_data["id"]
		self.vector = json_data["vector"]
		self.name = json_data.get("name")
		self.date = json_data.get("date")
		self.data = json_data.get("data")

	def __repr__(self):
		return f"Document(name={self.name}, date={self.date})"


class DataBase:
	"""
	Database class to store the data
	Note: for convenience, we are using a list to store the data
	"""
	def __init__(self):
		self.data = []

	def insert(self, data):
		self.data.append(data)

	def query(self, query: str):
		# do a vector search
		embedding = get_embedding(query)
		scores = []
		for d in self.data:
			x = np.array(d.vector)
			score = np.dot(x, embedding)
			scores.append(score)
		scores = np.array(scores)
		indices = np.argsort(scores)[::-1]
		return [self.data[i] for i in indices]

	def delete(self, query):
		self.data = [x for x in self.data if not query(x)]

	def save_data(self, filename):
		with open(filename, "w", encoding="utf-8") as f:
			json.dump([vars(d) for d in self.data], f, ensure_ascii=False, indent=4)


# singleton database
db = DataBase()

query_database = db.query
insert_database = db.insert
delete_database = db.delete

# load data
with open("json_files/database_test.json",
		  "r", encoding="utf-8") as f:
	data = json.load(f)
for d in data:
	insert_database(Document(d))


if __name__ == "__main__":
	# test
	query = input("Enter a query: ")
	results = query_database(query)
	print(results)
	# add more data
	insert_database(Document({"id": 100, "vector": [0.1, 0.2, 0.3], "name": "Event 1", "date": "2022-01-01"}))
	# save data
	db.save_data("json_files/database_test_saved.json")