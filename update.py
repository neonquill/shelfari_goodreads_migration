#!/usr/bin/env python

import csv

with open('My_Shelfari_Books.tsv', 'rb') as csvfile:
    csvreader = csv.DictReader(csvfile)
    for row in csvreader:
        print(row['Title'], row['Date Read'], row['Read'])
