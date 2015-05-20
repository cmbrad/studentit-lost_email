#!/usr/bin/env python3
from urllib.request import urlopen 
from lxml.html import parse

BASE_URL = "http://directory.unimelb.edu.au/?name="

def make_url(name):
    return BASE_URL + name.replace(" ", "+")

def get_from_directory(name):
    students = []
    url = make_url(name)
    root = parse(url).getroot()
    # Results are stored in a HTML table
    table = root.cssselect("#main-content > table")
    # If our query contains no results or too many results the table
    # will nto exist. Need to check for that
    rows = root.cssselect("#main-content > table")[0].findall("tr") if len(table) > 0 else [] 

    for row in rows[1:]:
        student = {}
        email = row.cssselect("td.email > a")[0].text
        given_name = row.cssselect("td.fn.n > span.given-name")[0].text
        family_name = row.cssselect("td.fn.n > span.family-name")[0].text

        full_name = "{} {}".format(given_name, family_name)

        student["name"] = full_name 
        student["email"] = email

        students.append(student)

    return students

if __name__ == "__main__":
	print(get_from_directory("Christopher Bradley"))
