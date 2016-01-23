#!/usr/bin/env python

import csv
import ConfigParser
import arrow
import time
import goodreads.client
import goodreads.review
import goodreads.book

def get_shelfari_books():
    """Read the exported book list."""

    books = {'isbn': {}, 'title': {}}
    dummy_isbn = 0

    with open('My_Shelfari_Books.tsv', 'rb') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            print (u"1111 Shelfari book: {} ({})"
                   .format(row['ISBN'],
                           row['Title'].decode('utf-8')))

            if row['ISBN']:
                isbn = row['ISBN']
            else:
                isbn = dummy_isbn
                dummy_isbn += 1

            book = {
                'isbn': isbn,
                'title': row['Title'],
                'plan_to_read': row['Plan To Read'],
                'reading': row['Currently Reading'],
                'read': row['Read'],
                'date_read': row['Date Read'],
                'rating': row['My Rating']
            }

            if isbn in books['isbn']:
                print "!!!! Duplicate S isbn: {}".format(isbn)
            books['isbn'][isbn] = book

            if row['Title'] in books['title']:
                print u"!!!! Duplicate S title: {}".format(row['Title'])
            books['title'][row['Title']] = book


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

    page = 0
    while True:
        page += 1
        params = {
            'v': 2,
            'shelf': '#ALL#',
            'per_page': 200,
            'page': page
        }
        resp = gc.session.get("review/list.xml", params)
        # @start, @end, @total.

        for r in resp['reviews']['review']:
            review = goodreads.review.GoodreadsReview(r)
            # print r
            book = goodreads.book.GoodreadsBook(review.book, gc)
            if book.title in books:
                print "!!!! Duplicate book: {}".format(book.title)

            print u"2222 Goodreads book: {} ({})".format(book.isbn, book.title)

            try:
                read_at = (arrow.get(review.read_at,
                                     'MMM DD HH:mm:ss Z YYYY')
                           .format('YYYY-MM-DD'))

            except TypeError:
                read_at = ''

            if not isinstance(book.isbn, basestring):
                print u"!!!! Unknown ISBN for {}".format(book.title)
                continue

            books[book.isbn] = {
                'review_id': review.gid,
                'read_at': read_at,
                'title': book.title,
                'rating': review.rating
            }

        # print resp['reviews']['@end'], resp['reviews']['@total']
        if resp['reviews']['@end'] == resp['reviews']['@total']:
            break

    return books

def update_review(gc, review_id, date_read, rating, shelf):
    params = {
        'id': review_id,
        'review[rating]': rating,
        'review[read_at]': date_read,
        'finished': 'true',
        'shelf': shelf
    }

    # XXX Hack because the goodreads lib doesn't support put requests.
    base = "http://www.goodreads.com/"
    path = "review/{}.xml".format(review_id)
    resp = gc.session.session.post(base + path, params=params, data={})
    print "Sent update"
    print resp

    # Make sure we don't send too fast.
    time.sleep(1)

def compare_books(gc, sbook, gbook):
    need_update = False
    diff = []

    if sbook['date_read'] != gbook['read_at']:
        diff.append("  Read: {} != {}.".format(sbook['date_read'],
                                               gbook['read_at']))
        need_update = True

    if sbook['rating'] != gbook['rating']:
        diff.append("  Rating: {} != {}.".format(sbook['rating'],
                                               gbook['rating']))
        need_update = True

    if need_update:
        print "Updating book: {}".format(sbook['title'])
        for line in diff:
            print line

        shelf = 'to-read'
        if sbook['reading']:
            shelf = 'currently-reading'
        if sbook['read']:
            shelf = 'read'

        update_review(gc, gbook['review_id'], sbook['date_read'],
                      sbook['rating'], shelf)

def update_all(gc, shelfari, goodreads):
    for isbn, shelfari_book in shelfari['isbn'].iteritems():
        try:
            goodreads_book = goodreads[isbn]
        except KeyError:
            print "!!!! Missing book: {} ({})".format(isbn,
                                                      shelfari_book['title'])
            continue

        # print "Found book: {}".format(shelfari_book['title'])
        compare_books(gc, shelfari_book, goodreads_book)

# main
gc = goodreads_connect()
shelfari = get_shelfari_books()
goodreads = get_goodreads_books(gc)

update_all(gc, shelfari, goodreads)
