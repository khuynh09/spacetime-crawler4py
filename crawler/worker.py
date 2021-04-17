from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time
from bs4 import BeautifulSoup
from utils import tokenizer

# .ics.uci.edu
# 


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.saved_urls = []
        self.word_freq = {}
        self.longest_page = [] # [page url, wordCount]
        self.subdomains = {}
        super().__init__(daemon=True)


    # def tokenize(content):
    #     for line in openedFile:
    #             tokens = re.sub(r'[^\w\s]|_', '', line).rstrip(
    #                 '\r\n').rstrip().split(" ")
    #             i = 0
    #             while i < len(tokens):
    #                 tokens[i] = tokens[i].lower()
    #                 i += 1
    def run(self):

        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)

            if 200 <= resp.status < 300 and resp.raw_response:
                soup  = BeautifulSoup(resp.raw_response.content, features="lxml")
                print(soup.get_text(separator=" "))
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
