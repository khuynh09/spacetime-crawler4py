import re
from urllib.parse import urlparse
from urllib.parse import urldefrag
from lxml.html.soupparser import fromstring
from lxml import etree


ics_urls = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu",
            ".stat.uci.edu", "today.uci.edu/department/information_computer_sciences/"]


def scraper(url, resp):

    links = extract_next_links(url, resp)
    return [urldefrag(link)[0] for link in links if is_valid(link)]


def extract_next_links(url, resp):
    # Implementation required.

    result = []
    try:
        #print(resp.status)
        if  resp.raw_response:
            html = resp.raw_response.content
            root = fromstring(html)
            html_string = etree.tostring(root).strip().decode("utf-8")

            hrefs = re.findall(r'href=".+" ', html_string)

            for href in hrefs:

                # print(h.split()[0])
                # parsed = urlparse(href.split()[0].strip("href=").strip('"'))
                # print(parsed)
                
                result.append(href.split()[0].strip("href=").strip('"'))

    except Exception as e:
        print(e)
        print()

        try:
            print(resp.status)
            if resp.raw_response:
                html = resp.raw_response.content
                root = etree.fromstring(html)
                html_string = etree.tostring(root).strip().decode("utf-8")

                hrefs = re.findall(r'href=".+" ', html_string)

                for href in hrefs:
                    # print(h.split()[0])
                    # parsed = urlparse(h.split()[0].strip("href=").strip('"'))
                    result.append( href.split()[0].strip("href=").strip('"'))

        except Exception as e:
            print(e)
            if "Opening and ending tag mismatch" in str(e):
                return []

    return result


def is_valid(url):

    try:
        defragged_url = urldefrag(url)[0]
        parsedURL = urlparse(defragged_url)

        if parsedURL.scheme not in set(["http", "https"]):
            return False

        is_ics_url = False

        correct_ics_url = parsedURL.scheme + parsedURL.netloc + parsedURL.path
        is_ics_url = any(
             ics_url in defragged_url for ics_url in ics_urls)

        if not is_ics_url:
            print(defragged_url + "\n")
            return False

        if re.match(
                r".*(\/events?\/|responds?|reply|replies|comments?|calenders?|\/css\/|\/js\/|\/pdf\/|\/gif\/|\/jpe?g\/|\/ico\/).*", url):
            return False

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz).*", defragged_url)

    except TypeError:
        print("TypeError for ", parsedURL)
        raise
