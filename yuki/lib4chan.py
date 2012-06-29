# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Functions to get some shit from 4chan.'''

from lxml import html
import requests

def get_threads(board, pages):
    '''Get all threads from a board up to a specified page
    
    TODO: Thread this, it's slow as shit.
    '''
    url = "http://boards.4chan.org/{0}/".format(board)
    threads = []
    for i in range(0, pages + 1):
        req = requests.get(url + str(i))
        page = html.fromstring(req.content)
        ops = page.find_class("post op")
        threads += ops
    return threads

def get_subject(thread):
    '''Get the subject of a thread.'''
    subject = thread.find_class("subject")
    subject = subject.pop(0)
    subject = subject.text_content()
    return subject

def check404(url):
    '''Check if a thread is still alive.'''
    req = requests.get(url)
    if req.status_code == 404:
        return True
    return False
