# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Functions to get some shit from 4chan.'''

import requests


class Thread(dict):
    '''Needed to be able to add Threads to a set.'''
    def __hash__(self):
        return self['no']


def get_threads(board, page=None):
    '''Get threads from a board.

    If page is specified, get that page's threads. Else get all (page=None).
    '''
    if page is None:
        url = "http://api.4chan.org/{0}/catalog.json".format(board)
    else:
        url = "http://api.4chan.org/{0}/{1}.json".format(board, page)

    content = requests.get(url).json()

    threads = []
    if page is None:
        for page in content:
            threads.extend(page['threads'])
    else:
        threads = content['threads']

    return [Thread(t) for t in threads]


def check404(url):
    '''Check if a thread is still alive.'''
    req = requests.get(url)
    if req.status_code == 404:
        return True
    return False
