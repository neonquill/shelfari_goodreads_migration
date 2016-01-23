#!/usr/bin/env python

import csv
import ConfigParser
import goodreads.client
import goodreads.review
import goodreads.book

def get_shelfari_books():
    """Read the exported book list."""

    books = {}

    with open('My_Shelfari_Books.tsv', 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            if row['Read']:
                books[row['Title']] = row['Date Read']

    return books

def goodreads_connect():
    """Connect to goodreads."""

    config = ConfigParser.RawConfigParser()
    config.read('goodreads.cfg')

    api_key = config.get('goodreads', 'api_key')
    api_secret = config.get('goodreads', 'api_secret')
    access_token = config.get('goodreads', 'access_token')
    access_token_secret = config.get('goodreads', 'access_token_secret')

    gc = goodreads.client.GoodreadsClient(api_key, api_secret)
    gc.authenticate(access_token, access_token_secret)

    return gc

def process_goodreads_reviews():
    resp = gc.session.get("review/list.xml", {'v': 2, 'per_page': 2})
    # @start, @end, @total.
    reviews = [goodreads.review.GoodreadsReview(r)
               for r in resp['reviews']['review']]
    for r in reviews:
        book = goodreads.book.GoodreadsBook(r.book, gc)
        print book.title, r.rating

shelfari = get_shelfari_books()
print shelfari
