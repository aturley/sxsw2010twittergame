import urllib2

game_tag = "#incol"

def get_data(url):
   resource = urllib2.urlopen(url)
   data = resource.read()
   return eval(data, {'null':None})

class TwitterGameVotes (object):
   def __init__(self, twitter, round):
       object.__init__(self)
       self.game_tag = game_tag
       self.twitter = twitter
       self.round = round
   def retrieve(self, since = None):
      on_page = 1
      print "########### getting page %d"%(on_page)
      search_results = self.twitter.start_search(self.game_tag, since)
      print "########### got page %d"%(on_page)
      on_page += 1
      while search_results.has_next_page():
         print "########### getting page %d"%(on_page)
         search_results.get_more_results()
         print "########### got page %d"%(on_page)
         on_page += 1
      game_results = [GameInput(r.from_user_id, r.created_at).parse_text(r.text) for r in search_results.results]
      # game_results are already sorted by date (latest first). So reverse the order and get the votes from the beginning.
      game_results.reverse()

      votes = {'A':0, 'B':0, 'C':0}

      for r in game_results:
         if r.is_valid() and r.round == self.round:
            votes[r.vote] += 1

      return votes

class GameInput (object):
   def __init__(self, player_id, created_at, round = None, vote = None):
       object.__init__(self)
       self.valid_votes = ['A', 'B', 'C']
       self.player_id = player_id
       self.created_at = created_at
       self.round = None
       self.vote = None
       if (type(round) == int):
           self.round = round
       if (vote in self.valid_votes):
           self.vote = vote
   def parse_text(self, text):
       self.round = None
       self.vote = None
       text_parts = text.split();
       try:
          vote_parts = text_parts[text_parts.index(game_tag):]
          if (len(vote_parts) >= 3):
             try:
                if (vote_parts[1].upper() in self.valid_votes):
                   self.vote = vote_parts[1].upper()
                   self.round = int(vote_parts[2])
             except Exception:
                # if anything goes wrong, just assume the input is invalid
                pass
       except Exception:
          # again, if anything goes wrong, just assume the input is invalid
          pass
       return self
   def is_valid(self):
       return not (self.round == None or self.vote == None)

class Tweet (object):
   def __init__(self, raw_tweet):
       object.__init__(self)
       self.from_user_id = raw_tweet['from_user_id']
       self.text = raw_tweet['text']
       self.created_at = raw_tweet['created_at']

class SearchResults (object):
   def __init__(self, raw_result):
       object.__init__(self)
       self.search_url = "http://search.twitter.com/search.json"
       self.get_data = get_data
       self.next_page_url = None
       if raw_result.has_key('next_page'):
           self.next_page_url = raw_result['next_page']
       self.results = [Tweet(r) for r in raw_result['results']]

   def get_more_results(self):
       if self.has_next_page():
          print "Getting '%s%s'"%(self.search_url, self.next_page_url)
          raw_result = self.get_data("%s%s"%(self.search_url, self.next_page_url))
          try:
             self.next_page_url = raw_result['next_page']
          except:
             self.next_page_url = None
          self.results.extend([Tweet(r) for r in raw_result['results']])
          
   def has_next_page(self):
       return not self.next_page_url == None

class Twitter (object):
   def __init__(self):
       object.__init__(self)
       self.search_url = "http://search.twitter.com/search.json"
       self.get_data = get_data

   def start_search(self, term, since = None):
       url = "%s?q=%s"%(self.search_url, urllib2.quote(term))
       if (since):
           url = "%s&since=%s"%(url, since)
       raw_result = self.get_data(url)
       return SearchResults(raw_result)
