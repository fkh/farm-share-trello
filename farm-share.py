from trello import TrelloClient
import inspect
import json
import sys
import argparse
import csv
import re
import copy

from settings import *


# Trello lists

# ids for confirmed member lists
# 54e4a423529df82c15d53b60 Check - paid in full 
# 54e4a428a30d6e71153809e8 Check - installments
# 54e4a41bc622aa6dfe2ef8f3 Online - paid
# 551ac183a3730ba8fe2ba1ca Level 1 paid deposit 

confirmed = ["54e4a423529df82c15d53b60","54e4a428a30d6e71153809e8","54e4a41bc622aa6dfe2ef8f3", "551ac183a3730ba8fe2ba1ca"]

# ids for possible member lists
# 54e4a3f92ae6750e126138d8 Inbox 
# 54eb610907daec1def86206c check - new
possible = ["54e4a3f92ae6750e126138d8","54eb610907daec1def86206c"]

# ids for level 1 list
# 54e4a3f92ae6750e126138d8 Inbox 
# 54eb610907daec1def86206c check - new
level_one = ["54e6c629990bb93f7acd3ba4"]

# ids for level 1 with no deposit
level_one_unpaid = ["54e6c629990bb93f7acd3ba4"]

# ids for level 1 with deposit paid
level_one_deposit = ["551ac183a3730ba8fe2ba1ca"]

# ids for people who haven't paid yet
# 54eb610907daec1def86206c check - new
new_check = ["54eb610907daec1def86206c"]

# for email searches
regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
    
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

def members_report (cards):

    members_csv = 'members.csv'

# prep a csv
    with open(members_csv, 'wb') as outputfile:
        wr = csv.writer(outputfile, quoting=csv.QUOTE_ALL)

        # write the header
        file_header = ["Name","Email","Fruit","Cheese","Value-added",
            "Volunteer","Level", "Membership status","List",
            "Partner 1", "Partner 1 email",
            "Partner 2", "Partner 2 email", 
            "Partner 3", "Partner 3 email",
            "Total","Payment by"]
        wr.writerow(file_header)
    
    # go through all cards
        for card in cards():
            details = []
            
            # get name after removing total cost info from card title
            name_list = card.name.split("$", 1)
            details.extend([name_list[0]]) 
            
            # get owner's email
            all_emails = list(extract_emails(card.description.lower()))
            if len(all_emails):
                details.append(all_emails[0])
            else:
                details.append(" ")

            # get share details
            details.append(share_finder(card.description, "Fruit share, 18 weeks", "Fruit"))
            details.append(share_finder(card.description, "Cheese share, 18 weeks", "Cheese"))
            details.append(share_finder(card.description, "Value-added share, 25 weeks", "Extras"))
            details.append(share_finder(card.description, "I'd rather pay $50 now", "NV"))

            # get level first
            for label in card.labels:
                
                this_label = label.get("name")
                if this_label[0:5] == "Level":
                    details.append(this_label)
            

            # membership status
            if card.idList in confirmed:
                details.append("Paid member")
            else:
                details.append("Unconfirmed")
            
            # Trello list 
            details.append(share_group(card.idList))
            
            # other members (up to three)
            details.append(name_extract(card.description, "Share partner #1 - name"))
            details.append(name_extract(card.description, "Share partner #1 - email"))
            details.append(name_extract(card.description, "Share partner #2 - name"))
            details.append(name_extract(card.description, "Share partner #2 - email"))
            details.append(name_extract(card.description, "Share partner #3 - name"))
            details.append(name_extract(card.description, "Share partner #3 - email"))
            
            #total membership amount
            if len(name_list) > 1 :
                details.extend([name_list[1]])
            
            # check/card payment last because not everyone has this label set
            for label in card.labels:
                this_label = label.get("name")
                if (this_label == "check") or (this_label == "online"):
                    details.append(this_label)
            
            # write it
            wr.writerow(details)
        
## summary of confirmed members 
def confirmed_members (blists):

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

    volunteers_csv = 'volunteers.csv'

# prep a csv
    with open(volunteers_csv, 'wb') as outputfile:
        wr = csv.writer(outputfile, quoting=csv.QUOTE_ALL)

# what are all the possible volunteer items?
        roles = ["Helping with fundraising", "Organizing events and parties","Communications and social media","Cooking demos","Bake sales","Bookkeeping and membership management","Volunteering with local projects","Building connections between the farm share and other local projects","Joining the core organizing team","Something else (please email us!)"]
        
        export_roles = list(roles)
        export_roles[:0] = ["Name","Email","Card"]
   
    # write the roles
        wr.writerow(export_roles)

        interested_volunteers = 0

    # go through all cards
        for card in cards():
            if card.idList in confirmed: 
                
                roles_chosen = 0
                details = []
                # get name after removing total cost info from card title
                name_list = card.name.split("$", 1)
                details.extend([name_list[0]])
                
                # get owner's email
                all_emails = list(extract_emails(card.description.lower()))
                if len(all_emails):
                    details.append(all_emails[0])
                else:
                    details.append(" ")
                
                # card id
                details.extend([card.id])
                
                # info on roles
                for role in roles:
                    if role in card.description:
                        roles_chosen += 1
                        details.extend([1])
                    else:
                        details.extend([0])
                
                # write it
                if roles_chosen > 0:
                    interested_volunteers += 1
                    wr.writerow(details)
        
        # report back
        print("Wrote info on {0} possible volunteers to {1}".format(interested_volunteers, volunteers_csv))
    
def emails(cards):
    print "Writing emails to a csv file"

    # paid members
    with open('paid.csv', 'wb') as paid_file:
        with open('unpaid.csv', 'wb') as possible_file:
            with open('all.csv', 'wb') as all_file:
                paid_email_list = list()
                possible_email_list = list()
                for card in cards():
                    if card.idList in confirmed:
                        for email in (extract_emails(card.description.lower())):
                            paid_email_list.append(email)
                            paid_file.write('{0}\n'.format(email))
                            all_file.write('{0}\n'.format(email))
                    if card.idList in new_check:
                        for email in (extract_emails(card.description.lower())):
                            possible_email_list.append(email)
                            possible_file.write('{0}\n'.format(email))
                            all_file.write('{0}\n'.format(email))
                print "Extracted {0} emails of paid members, saved to paid.csv".format(len(paid_email_list))
                print "Extracted {0} emails of unpaid possible members, saved to unpaid.csv".format(len(possible_email_list))
                print "all.csv contains both lists"

def emails_level_ones(cards):
    print "Writing level 1 emails to a csv file"
    with open('level-1-deposit.csv', 'wb') as paid_file:
        with open('level-1-unpaid.csv', 'wb') as possible_file:
            paid_email_list = list()
            possible_email_list = list()
            for card in cards():
                if card.idList in level_one_deposit:
                    for email in (extract_emails(card.description.lower())):
                        paid_email_list.append(email)
                        paid_file.write('{0} {1}\n'.format(card.name, email))
                if card.idList in level_one_unpaid:
                    for email in (extract_emails(card.description.lower())):
                        possible_email_list.append(email)
                        possible_file.write('{0} {1}\n'.format(card.name, email))
            print "Extracted {0} emails of level 1 members, saved to level-1-deposit.csv".format(len(paid_email_list))
            print "Extracted {0} emails of unpaid level 1 members, saved to level-1-unpaid.csv".format(len(possible_email_list))


# -- helpers --

# thanks to https://gist.github.com/dideler/5219706
def extract_emails(text): 
    return (email[0] for email in re.findall(regex, text))

# is this person getting fruit, cheese, etc?
def share_finder(card_description, share_phrase, for_report):
    
    if card_description.find(share_phrase) > 0 :
        return for_report
    else:
        return " "

# look up the list name to spare the trello api from calls to blist directly
def share_group(card_id_list):
    for group_id, name in groups.iteritems():
        if group_id == card_id_list:
            return name

# get and clean up share members
def name_extract(card_description, name_label):
    for item in card_description.split("\n"):
        if name_label in item:
            clean_name = item.split(name_label,1)[1]
            if ":" in clean_name:
                clean_name = clean_name.split(":",1)[1]
            return clean_name.strip()

# -- main --

# arguments
parser = argparse.ArgumentParser(description='Helpers for farm share membership ')

# overall totals
parser.add_argument(
    '--totals',
    dest='totals',
    action='store_true',
    default=False,
    help='Report out totals in each list.')

# confirmed members
parser.add_argument(
    '--confirmed',
    dest='confirmed',
    action='store_true',
    default=False,
    help='How many confirmed members?')

# possible members
parser.add_argument(
    '--possible',
    dest='possible',
    action='store_true',
    default=False,
    help='How many possible members?')
    
# level one totals
parser.add_argument(
    '--ones',
    dest='ones',
    action='store_true',
    default=False,
    help='How many Level One?')

# get volunteer summary
parser.add_argument(
    '--volunteers',
    dest='volunteers',
    action='store_true',
    default=False,
    help='Collect details of all the volunteers and their interests')

# get emails
parser.add_argument(
    '--emails',
    dest='emails',
    action='store_true',
    default=False,
    help='All emails for confirmed members')

# get all members
parser.add_argument(
    '--members',
    dest='members',
    action='store_true',
    default=False,
    help='Full member report')

args = parser.parse_args()

# Trello
client = TrelloClient(
  api_key = settings_api_key,
  api_secret = settings_api_secret,
  token= settings_token,
  token_secret= settings_token_secret
)

board = client.get_board("dKKiaWEP")
blists = copy.deepcopy(board.all_lists)
cards = copy.deepcopy(board.all_cards)

# in preparation, copy the list details, must be a better way to do this
groups = {}
for blist in blists():
    groups[str(blist.id)] = str(blist.name)


# get a full report from all lists
if args.totals:
    membersummary(blists)

# get the total confirmed members
if args.confirmed:
    confirmed_members(blists)

# get total possible members
if args.possible:
    possible_members(blists)

# get level one members
if args.ones:
    level_one_members(blists)
    emails_level_ones(cards)

# print out volunteer interests
if args.volunteers:
    volunteers(cards)

# extract all the emails
if args.emails:
    emails(cards)
    
# list all the members
if args.members:
    members_report(cards)
