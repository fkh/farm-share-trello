from trello import TrelloClient
import inspect
import json
import sys, getopt
import csv

from settings import *

## print out all the lists in csv-friendly format
def membersummary (blists):
    for blist in blists():
        cards = board.all_cards

        levelone = 0
        leveltwo = 0
        levelthree = 0
        levelfour = 0

        for card in cards():
            if blist.id == card.idList:
                for label in card.labels:
                  if label.get("name") == "Level 1":
                      levelone = levelone + 1
                  if label.get("name") == "Level 2":
                      leveltwo = leveltwo + 1
                  if label.get("name") == "Level 3":
                      levelthree = levelthree + 1
                  if label.get("name") == "Level 4":
                      levelfour = levelfour + 1
        if levelone > 0:
            print "{0}, {1}, L1, {2} ".format(blist.id, blist.name, levelone)
        if leveltwo > 0:
            print "{0}, {1}, L2, {2} ".format(blist.id, blist.name, leveltwo)
        if levelthree > 0:
            print "{0}, {1}, L3, {2} ".format(blist.id, blist.name, levelthree)
        if levelfour > 0:
            print "{0}, {1}, L4, {2} ".format(blist.id, blist.name, levelfour)
    return

## summary of confirmed members 
def confirmed_members (blists):

# ids for confirmed member lists
# 54e4a423529df82c15d53b60 Check - paid in full 
# 54e4a428a30d6e71153809e8 Check - installments
# 54e4a41bc622aa6dfe2ef8f3 Online - paid

    confirmed = ["54e4a423529df82c15d53b60","54e4a428a30d6e71153809e8","54e4a41bc622aa6dfe2ef8f3"]

# totals for confirmed members
    levelone = 0
    leveltwo = 0
    levelthree = 0
    levelfour = 0

# loop through lists
    for blist in blists():
        if blist.id in confirmed: 
            cards = board.all_cards
            for card in cards():
                if blist.id == card.idList:
                    for label in card.labels:
                      if label.get("name") == "Level 1":
                          levelone = levelone + 1
                      if label.get("name") == "Level 2":
                          leveltwo = leveltwo + 1
                      if label.get("name") == "Level 3":
                          levelthree = levelthree + 1
                      if label.get("name") == "Level 4":
                          levelfour = levelfour + 1

# report out the totals

    print "Paid:"
    if levelone > 0:
        print "L1, {0} ".format(levelone)
    if leveltwo > 0:
        print "L2, {0} ".format(leveltwo)
    if levelthree > 0:
        print "L3, {0} ".format(levelthree)
    if levelfour > 0:
        print "L4, {0} ".format(levelfour)
    return

## summary of possible members 
def possible_members (blists):

# ids for possible member lists
# 54e4a3f92ae6750e126138d8 Inbox 
# 54eb610907daec1def86206c check - new

    possible = ["54e4a3f92ae6750e126138d8","54eb610907daec1def86206c"]

# totals for possible members
    levelone = 0
    leveltwo = 0
    levelthree = 0
    levelfour = 0

# loop through lists
    for blist in blists():
        if blist.id in possible: 
            cards = board.all_cards
            for card in cards():
                if blist.id == card.idList:
                    for label in card.labels:
                      if label.get("name") == "Level 1":
                          levelone = levelone + 1
                      if label.get("name") == "Level 2":
                          leveltwo = leveltwo + 1
                      if label.get("name") == "Level 3":
                          levelthree = levelthree + 1
                      if label.get("name") == "Level 4":
                          levelfour = levelfour + 1

# report out the totals

    print "New/no check yet:"
    if levelone > 0:
        print "L1, {0} ".format(levelone)
    if leveltwo > 0:
        print "L2, {0} ".format(leveltwo)
    if levelthree > 0:
        print "L3, {0} ".format(levelthree)
    if levelfour > 0:
        print "L4, {0} ".format(levelfour)
    return
    
## summary of possible members 
def level_one_members (blists):

    # ids for level 1 list
    # 54e4a3f92ae6750e126138d8 Inbox 
    # 54eb610907daec1def86206c check - new

    level_one = ["54e6c629990bb93f7acd3ba4"]

    # totals for possible members
    levelone = 0

    # loop through lists
    for blist in blists():
        if blist.id in level_one: 
            cards = board.all_cards
            for card in cards():
                if blist.id == card.idList:
                    for label in card.labels:
                      if label.get("name") == "Level 1":
                          levelone = levelone + 1

    # report out the totals
    if levelone > 0:
        print "Level 1: {0} ".format(levelone)
    return

# unfinished csv export
def printcsv (blists):
    
    for blist in blists():
        for card in cards():
            if blist.id == card.idList:
                cardrow = {'name': card.name}
    return 

# report out volunteer interests

def volunteers (cards):
    
    print("Writing info on volunteer assignments to volunteers.csv")
    
    confirmed = ["54e4a423529df82c15d53b60","54e4a428a30d6e71153809e8","54e4a41bc622aa6dfe2ef8f3"]

# prep a csv
    with open('volunteers.csv', 'wb') as outputfile:
        wr = csv.writer(outputfile, quoting=csv.QUOTE_ALL)

# what are all the possible volunteer items?
        roles = ["Helping with fundraising", "Organizing events and parties","Communications and social media","Cooking demos","Bake sales","Bookkeeping and membership management","Volunteering with local projects","Building connections between the farm share and other local projects","Joining the core organizing team","Something else (please email us!)"]
        
        export_roles = list(roles)
        export_roles[:0] = ["Name","Date"]
   
    # write the roles
        wr.writerow(export_roles)

    # go through all cards
        for card in cards():
            if card.idList in confirmed: 
                details = []
                name_list = card.name.split("$", 1)
                details.extend([name_list[0]])
                details.extend([card.id])
                for role in roles:
                    if role in card.description:
                        details.extend([1])
                    else:
                        details.extend([0])
                wr.writerow(details)

# main

client = TrelloClient(
  api_key = settings_api_key,
  api_secret = settings_api_secret,
  token= settings_token,
  token_secret= settings_token_secret
)

board = client.get_board("dKKiaWEP")

blists = board.all_lists

# get a full report from all lists
# membersummary(blists)

# get the total confirmed members
# confirmed_members(blists)

print " " 

# get total possible members
# possible_members(blists)

print " " 

# get level one members
# level_one_members(blists)

# print out volunteer interests
cards = board.all_cards
volunteers(cards)