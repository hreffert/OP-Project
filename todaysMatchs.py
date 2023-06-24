from results import makeRequest, bets
from datetime import datetime
import json
import html
import time
import concurrent.futures
from configparser import ConfigParser
from common import getValue

config_object = ConfigParser()
config_object.read("config.ini")

#threadcounts
threadCounts = config_object['ThreadCounts']
maxT = int(threadCounts['todaysMatch'])

#Credentials
credentails = config_object['Credentials']
mongoUri = credentails['mongo']

site = 'https://www.oddsportal.com'

games = ['football']
  
def scrap(game, obj):
  try:
    print("SCRAPING FROM:", game)
    r = makeRequest(f'https://www.oddsportal.com/matches/{game}')
    htmlData = r.text
    ajax = getValue('<next-matches-wrapper :data-next="(.*?)">', htmlData)
    if ajax == None:
      return False
    urlRe = getValue('/(\d+)./"\s*,\s*"hash"\s*:\s*"(.*?)"', html.unescape(ajax))
    url = f"https://www.oddsportal.com/ajax-nextgames/{urlRe[0]}/5.5/1/{datetime.today().strftime('%Y%m%d')}/yjfd0.dat?_={round(datetime.now().timestamp())}"
    data = makeRequest(url, 'https://www.oddsportal.com/matches/tennis').json()
    #slugs = [site + x['url'] for x in data['d']['rows']]
    allUrls = []
    for one in data['d']['rows']:
      url = ''
      if 'url' in one:
        url = site + one['url']
        if url in allUrls:
          continue
        allUrls.append(url)
      obj['races'].append({'raceURL':url, 'country':one.get('country-name'), "league": getValue('https://www\.oddsportal\.com/.*?/.*?/(.*?)/', url), 'game':game, 'Odds':bets(url), 'Time':one.get('date-start-base'), 'Home':one.get('home-name'), 'Away': one.get('away-name'), 'H Score':one.get('homeResult'), 'A Score':one.get('awayResult')})
      #break #testing
  except Exception as ex:
    print(ex)

  
def start(db):
  collection = db.ODDS
  obj = {'yearURL':'', 'year':'', 'races':[]}
  #'''
#  executor = concurrent.futures.ThreadPoolExecutor(max_workers=maxT)
  if True:
#  with concurrent.futures.ThreadPoolExecutor(max_workers=maxT) as executor:
    for g in games:
      #executor.submit(scrap, g, obj)
      scrap(g, obj)

  if collection.find_one({'yearURL':''}) == None:
    collection.insert_one(obj)
    print("INSERTING INTO DB")
  else:
    collection.update_one({'yearURL':obj['yearURL']}, {'$set':obj})
    print("UPDATEING INTO DB")
  '''
  for x in games:
    scrap(x, obj) 
  '''
    
if __name__ == "__main__":
  start(db)
