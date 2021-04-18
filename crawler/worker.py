from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time
from bs4 import BeautifulSoup
from utils import tokenizer
import re
from urllib.parse import urlparse
from urllib.parse import urldefrag

# .ics.uci.edu
# 


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.saved_urls = []
        self.word_freq = {}
        self.longest_page = ["", 0] # [page url, wordCount]
        self.subdomains = {}
        self.stop_words = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
                "as", "at", "be", "because", "been",
                "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
                "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
                "from", "further", "had", "hadn't", "has", "hasn't",
                "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers",
                "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
                "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
                "me", "more", "most", "mustn't", "my",
                "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
                "ours", "ourselves", "out",
                "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
                "so", "some", "such", "than", "that", "that's", "the", "their",
                "theirs", "them", "themselves", "then", "there",
                "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to",
                "too",
                "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
                "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
                "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
                "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"]

        super().__init__(daemon=True)


    def tokenize(self, url, content):
        token_list = []
        for line in content.split():
            tokens = re.sub(r'[^\w\s]|_', '', line).rstrip(
                '\r\n').rstrip().split(" ")
            i = 0
            while i < len(tokens):
                tokens[i] = tokens[i].lower()
                i += 1
            token_list.extend(tokens)
            

        for token in token_list:
            if (token in self.word_freq):
                self.word_freq[token] += 1
            else:
                self.word_freq[token] = 1

        if len(token_list) > self.longest_page[1]:
            self.longest_page = [url, len(token_list)]
        return token_list

        



    def run(self):

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)


            #netloc :  www.stat.uci.edu
            #https://www.stat.uci.edu/
            #http://www.stat.uci.edu/ 
            if 200 <= resp.status < 300 and resp.raw_response:
                soup  = BeautifulSoup(resp.raw_response.content, features="lxml")
                netloc = urlparse(tbd_url).netloc
                
                if "ics.uci.edu" in netloc:

                    if netloc not in self.subdomains:
                        self.subdomains[netloc] = 1
                    else:
                        self.subdomains[netloc] += 1
                

                #filtering out "low quality" content
                token_list = self.tokenize(tbd_url, soup.get_text(separator=" "))
                #less than 300 words
                if(len(token_list) <=  300):
                    continue

                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                
                
                scraped_urls = scraper(tbd_url, resp)
                # print(self.saved_urls)
                for scraped_url in scraped_urls:
                    
                    if scraped_url not in self.saved_urls:
                        
                        self.frontier.add_url(scraped_url)
                        self.saved_urls.append(scraped_url)

                        
                        
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)

        sortedWords = sorted(self.word_freq.items(), key=lambda x: x[1], reverse=True)
        top50 = []
        i = 0
        while len(top50) < 50:
            if sortedWords[i][0] not in self.stop_words:
                top50.append(sortedWords[i])
            i += 1
        print(len(self.saved_urls)) #unique pages
        print(top50) #50 most common words
        print(self.longest_page[0]) ## longest page in terms of words

        for k,v in sorted(self.subdomains.items()): ## number of self domains
            print("{}, {}".format(k,v))

        