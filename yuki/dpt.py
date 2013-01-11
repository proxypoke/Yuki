# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Check for and get DPTs on /g/.'''

from . import lib4chan

import re

# possible DPTs
_candidates = set()
# threads that have 404'd since the last check
_404 = set()
# new threads since the last check
_new = set()

# thread url template
thread_url = 'https://boards.4chan.org/g/res/{0}'


# regex patterns for matching against the thread subject
# TODO: move this out into a config file
_subjects = [re.compile("daily programming thread$", re.I),
             re.compile("DPT")
             ]
# hashes for matching against the thread image
# TODO: create a folder of such images, and hash them on startup
_images = ['E7lDroAeC0ZDx53Y2RXeYQ==',
           ]

def get_dpt_urls(check=True):
    '''Return all possible DPT threads by url.'''
    if check:
        check_for_dpt()
    return [thread_url.format(thread['no']) for thread in _candidates]


def get_dpts(check=True):
    '''Return all possible DPT threads.'''
    if check:
        check_for_dpt()
    return list(_candidates)


def get_404():
    '''Get all 404'd threads since the last check.'''
    return list(_404)


def get_new():
    '''Get all new threads since the last check.'''
    return list(_new)


def check_for_dpt():
    '''Check for daily programming threads.

    Also check whether any existing ones have 404'd.
    '''
    # throw out 404'd threads
    _404.clear()
    for thread in _candidates:
        url = thread_url.format(thread['no'])
        if lib4chan.check404(url):
            print("Thread 404'd: {0}".format(hash(thread)))
            _404.add(thread)
            _candidates.discard(thread)

    # get new ones
    _new.clear()
    threads = lib4chan.get_threads(board='g')
    for thread in threads:
        if match_subject(thread) or match_image(thread):
            # FIXME: something goes wrong here. Threads which are posted in
            # somehow get counted as new threads. This shouldn't happen.
            for thread in _candidates:
                print(hash(thread))
            if thread not in _candidates:
                print("New thread: {0}".format(hash(thread)))
                _new.add(thread)
            _candidates.add(thread)


def match_subject(thread):
    '''Check if a thread might be a DPT by its subject.'''
    if not 'sub' in thread.keys():
        return False
    for sub in _subjects:
        if sub.match(thread['sub']):
            return True
    return False


def match_image(thread):
    '''Check if a thread might be a DPT by its image.

    Can also be used to see if a DPT uses an established image.

    This uses hashes of established DPT images to check.'''
    if not 'md5' in thread.keys():
        return False
    return thread['md5'] in _images
