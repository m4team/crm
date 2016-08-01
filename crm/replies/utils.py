from HTMLParser import HTMLParser
import re

def extract_img_html(html):
    p = re.compile(r'<img.*?>')
    return p.sub('', html)

def extract_link_html(html):
    p = re.compile(r'<a href.*?a>')
    return p.sub('', html)

