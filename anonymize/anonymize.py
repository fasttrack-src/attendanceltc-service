import csv
import hashlib
import base64
import random

names = set()
mapped_names = {}
mapped_ids = {}
mapped_barcodes = {}
mapped_cas_numbers = {}

def import_fake_names():
	with open("names") as data:
		for name in data:
			firstname, lastname = name.strip().split('\t')

			names.add((firstname, lastname))

def anonymize():
	with open("UOG_MATHS_CLASSES2-2754607.csv") as in_csv, \
		open('anonymized.csv', 'w', newline='') as out_csv:

		fields = ("Subject", "Catalog", "Long Title", "ID", "Last", "First Name", "Year",
			"Institution", "Component", "Lecture", "Barcode", "CAS Number")

		reader = csv.DictReader(in_csv)
		writer = csv.DictWriter(out_csv, fieldnames = fields)

		writer.writeheader()

		for row in reader:
			# Anonymize name
			name = (row["First Name"], row["Last"])

			if name not in mapped_names:
				mapped_names[name] = names.pop()

			row["First Name"], row["Last"] = mapped_names[name]

			# Anonymize student ID
			if row["ID"] not in mapped_ids:
				while True:
					new_id = ''.join(["%s" % random.randint(0, 9) for num in range(0, 7)])
					
					if new_id not in mapped_ids.values():
						mapped_ids[row["ID"]] = new_id
						break

			# Anonymize barcodes
			if row["Barcode"] not in mapped_barcodes:
				while True:
					new_id = ''.join(["%s" % random.randint(0, 9) for num in range(0, 14)])
					
					if new_id not in mapped_ids.values():
						mapped_barcodes[row["Barcode"]] = new_id
						break

			# Anonymize barcodes
			if row["CAS Number"] and row["CAS Number"] not in mapped_cas_numbers:
				while True:
					new_id = ''.join(["%s" % random.randint(0, 9) for num in range(0, 14)])
					
					if new_id not in mapped_ids.values():
						mapped_cas_numbers[row["CAS Number"]] = new_id
						break

			row["ID"] = mapped_ids[row["ID"]]
			row["Barcode"] = mapped_barcodes[row["Barcode"]]

			if row["CAS Number"]:
				row["CAS Number"] = mapped_cas_numbers[row["CAS Number"]]

			writer.writerow({field : row[field] for field in fields})

import_fake_names()
anonymize()