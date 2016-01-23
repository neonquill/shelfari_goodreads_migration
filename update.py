#!/usr/bin/env python

import csv
import ConfigParser
import arrow
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
                books[row['ISBN']] = {
                    'title': row['Title'],
                    'date_read': row['Date Read'],
                    'rating': row['My Rating']
                }

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

def get_goodreads_books(gc):
    """Get the reviews from goodreads."""

    books = {}

    resp = gc.session.get("review/list.xml", {'v': 2, 'per_page': 2})
    # @start, @end, @total.

    for r in resp['reviews']['review']:
        review = goodreads.review.GoodreadsReview(r)
        print r
        book = goodreads.book.GoodreadsBook(review.book, gc)
        if book.title in books:
            print "!!!! Duplicate book: {}".format(book.title)
        print "111 Shelfari book: {}".format(book.title)

        try:
            read_at = arrow.get(review.read_at,
                                'MMM DD HH:mm:ss Z YYYY').format('YYYY-MM-DD')
        except TypeError:
            read_at = ''

        books[book.isbn] = {
            'review_id': review.gid,
            'read_at': read_at,
            'title': book.title,
            'rating': review.rating
        }

    return books

def update_review(gc, review_id, date_read, rating):
    params = {
        'id': review_id,
        'review[rating]': rating,
        'review[read_at]': date_read,
        'finished': 'true',
        'shelf': 'read'
    }
    # XXX Hack because the goodreads lib doesn't support put requests.
    base = "http://www.goodreads.com/"
    path = "review/{}.xml".format(review_id)
    resp = gc.session.session.post(base + path, params=params, data={})
    print "Sent update"
    print resp

def compare_books(gc, sbook, gbook):
    need_update = False

    if sbook['date_read'] != gbook['read_at']:
        print "  Read: {} != {}.".format(sbook['date_read'], gbook['read_at'])
        need_update = True

    if sbook['rating'] != gbook['rating']:
        print "  Rating: {} != {}.".format(sbook['rating'], gbook['rating'])
        need_update = True

    if need_update:
        update_review(gc, gbook['review_id'], sbook['date_read'],
                      sbook['rating'])

def update_all(gc, shelfari, goodreads):
    for isbn, shelfari_book in shelfari.iteritems():
        try:
            goodreads_book = goodreads[isbn]
        except KeyError:
            #print "!!!! Missing book: {}".format(shelfari_book['title'])
            continue

        print "Found book: {}".format(shelfari_book['title'])
        compare_books(gc, shelfari_book, goodreads_book)

# main
gc = goodreads_connect()
shelfari = get_shelfari_books()
goodreads = get_goodreads_books(gc)

update_all(gc, shelfari, goodreads)
