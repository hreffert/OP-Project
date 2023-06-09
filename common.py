import time
import requests
import random
import re


class ProxyServer:    
  
  def __init__(self):
    self.enableProxies = False
    
    if self.enableProxies == True:
      with open("proxies.txt") as f:
        self.realProxies = []
        for x in f.readlines():
          self.realProxies.append(x.strip())
      print("Initiated ProxyServer - Set proxies = ", len(self.realProxies))
  
  def get_request(self, url, user_agent=False, proxyAVA=True):
    if url in [None, '', ' ', [], {}]:
      print('invalid url:', url)
      return ''
    proxyObj = {}
    i = 0
    while i <= 50:
      i = i + 1
      try:
        if self.enableProxies == True and proxyAVA == True: 
          try:
            proxy = random.choice(self.realProxies)
            print("Current proxy: ", proxy)
            proxyObj = {"all://": 'http://'+proxy}
          except Exception as ex:
            print(ex)
        
        if user_agent == False:
          user_agent = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

        print("GET", url)
        r = requests.get(url, headers=user_agent, proxies=proxyObj)
        time.sleep(5)
        return r
      except Exception as ex:
        print("Exception in get_request function:",ex,", Trying again in 10 second")
        time.sleep(10)
        pass
    

  def post_request(self, url, json, user_agent=False, proxyAVA=True, data=False):
    if url in [None, '', ' ', [], {}]:
      print('invalid url:', url)
      return ''
    proxyObj = {}
    i = 0
    while i <= 50:
      i = i + 1
      try:
        if self.enableProxies == True and proxyAVA == True:        
          try:
            proxy = random.choice(self.realProxies)
            proxyObj = {"all://": 'http://'+proxy}
          except Exception as ex:
            print("Proxy error: ", ex)
        
        if user_agent == False:
          user_agent = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        
        
        print("POST", url, data, json)
        if data:
          r = requests.post(url, headers=user_agent, proxies=proxyObj, data=data)
        else:
          r = requests.post(url, headers=user_agent, proxies=proxyObj, json=json)
        
        return r
      except Exception as ex:
        print("Exception in post_request function:",ex,", Trying again in 10 second")
        time.sleep(10)
        pass
        
        
def getValue(regexVal, strVal, allR = "no"): 
  href = re.findall(regexVal, strVal, re.MULTILINE | re.IGNORECASE | re.DOTALL)
  if len(href) == 0:
    return None
  else:
    if allR == "yes":
      return href
    else:  
      return href[0]
        
        
