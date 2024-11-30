import requests
from bs4.element import Comment
from bs4 import BeautifulSoup
import os

ARTISAN_URL = "https://artisan.co"
response = requests.get(ARTISAN_URL)
soup = BeautifulSoup(response.content, "html.parser")


# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


urls = [ARTISAN_URL]
visted_urls = set([])
text_list = []


while len(urls) != 0:
    # get the page to visit from the list
    current_url = urls.pop()
    try:
        response = requests.get(current_url)
    except:
        print("Falied to access %s" % current_url)
        continue
    soup = BeautifulSoup(response.content, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    text = [t.strip() for t in visible_texts if len(t.strip()) > 0]
    if len(text) > 0:
        text_list.append(' '.join(text))
    for link in soup.find_all('a'):
        link_url = link.get('href')
        if link_url is not None and link_url.startswith('http') and 'artisan' in link_url.lower() and link_url not in visted_urls:
            urls.append(link_url)
            visted_urls.add(link_url)
    print(current_url)
    # print(' '.join(text))

docs = '\n'.join(text_list)

docs_path = os.path.join(os.path.dirname(__file__), 'data', 'docs.txt')
f = open(docs_path, "a")
f.write(docs)
f.close()