#!/usr/bin/env python

import csv
import ConfigParser
import goodreads.client
import goodreads.review
import goodreads.book

# Read the exported book list.
with open('My_Shelfari_Books.tsv', 'rb') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        pass
        #print(row['Title'], row['Date Read'], row['Read'])


# Connect to goodreads.
config = ConfigParser.RawConfigParser()
config.read('goodreads.cfg')

api_key = config.get('goodreads', 'api_key')
api_secret = config.get('goodreads', 'api_secret')
access_token = config.get('goodreads', 'access_token')
access_token_secret = config.get('goodreads', 'access_token_secret')

gc = goodreads.client.GoodreadsClient(api_key, api_secret)
gc.authenticate(access_token, access_token_secret)
#print gc.auth_user()

resp = gc.session.get("review/list.xml", {'v': 2, 'per_page': 2})
# @start, @end, @total.
reviews = [goodreads.review.GoodreadsReview(r)
           for r in resp['reviews']['review']]
for r in reviews:
    book = goodreads.book.GoodreadsBook(r.book, gc)
    print book.title, r.rating
