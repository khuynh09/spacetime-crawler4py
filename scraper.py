import re
from urllib.parse import urlparse
from lxml.html.soupparser import fromstring
from lxml.etree import tostring
from lxml import etree

ics_urls = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu", "today.uci.edu/department/information_computer_sciences/"]

def scraper(url, resp):

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.

    result = []
    try:

        if resp.raw_response:
            html = resp.raw_response.content
            root = fromstring(html)
            html_string = tostring(root).strip().decode("utf-8") 


            hrefs = re.findall(r'href=".+" ', html_string)

            for href in hrefs:
                # print(h.split()[0])
                # parsed = urlparse(h.split()[0].strip("href=").strip('"'))
                result.append(href.split()[0].strip("href=").strip('"'))

    except Exception as e:
        print(e)
        print()

        try: 
            if resp.raw_response:
                html = resp.raw_response.content
                root = etree.fromstring(html)
                html_string = etree.tostring(root).strip().decode("utf-8") 


                hrefs = re.findall(r'href=".+" ', html_string)

                for href in hrefs:
                    # print(h.split()[0])
                    # parsed = urlparse(h.split()[0].strip("href=").strip('"'))
                    result.append(href.split()[0].strip("href=").strip('"'))

        except Exception as e:
            print(e)
            if "Opening and ending tag mismatch" in str(e):
                return []
            


    return result

def is_valid(url):
    

    try:
        parsed = urlparse(url)

        if parsed.scheme not in set(["http", "https"]):
            return False

        is_ics_url = False

        correct_ics_url = parsed.scheme + parsed.netloc + parsed.path
        is_ics_url =  any(url in correct_ics_url for url in ics_urls)

        if not is_ics_url:
            return False 

        # if re.match(r".*respond.*|.*reply.*|.*comment.*",parsed.query) or re.match(r".*pdf.*|.*respond.*|.*reply.*|.*comment.*",url):
        #     return False

        return not re.match(
            r".*\.(respond|reply|comment|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz).*", url)

    except TypeError:
        print ("TypeError for ", parsed)
        raise