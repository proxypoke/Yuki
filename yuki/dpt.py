# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Check for and get DPTs on /g/.'''

from . import lib4chan

import re

# possible DPTs
_candidates = set()

# thread url template
_thread_url = 'https://boards.4chan.org/g/res/{0}'


# TODO: move this out into a config file
# regex patterns for matching against the thread subject
_subjects = [re.compile("daily programming thread$", re.I),
             re.compile("DPT")
             ]
# hashes for matching against the thread image
# TODO: create a folder of such images, and hash them on startup
_images = [b'E7lDroAeC0ZDx53Y2RXeYQ==\n',
           ]


class Thread(dict):
    '''Needed to be able to add Threads to a set.'''
    def __hash__(self):
        return self['no']


def get_dpt_urls():
    '''Return all possible DPT threads by url.'''
    check_for_dpt()

    return [_thread_url.format(thread['no']) for thread in _candidates]


def check_for_dpt():
    '''Check for daily programming threads.

    Also check whether any existing ones have 404'd.
    '''
    global _candidates

    # throw out 404'd threads
    for thread in _candidates:
        url = _thread_url.format(thread['no'])
        if lib4chan.check404(url):
            _candidates.discard(thread)

    # get new ones
    threads = lib4chan.get_threads(board='g')
    for thread in threads:
        if match_subject(thread) or match_image(thread):
            _candidates.add(Thread(thread))


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

    This uses hashes of established DPT images to check.'''
    if not 'md5' in thread.keys():
        return False
    for hash_ in _images:
        if hash_ == thread['md5']:
            return True
    return False




#class _DPT(object):
#    '''Class that wraps a DPT, storing whether it exists and its url.'''
#    def __init__(self, irc, channels):
#        # IRC object
#        self._irc = irc
#        # channels to report to
#        self._channels = channels.split(',')
#        # thread url
#        self._url = None
#        # html object
#        self._thread = None
#        # fetch lock.
#        self._fetching = False
#        # subject regex
#        self._pattern = re.compile("daily programming thread$", re.I)
#
#    def update(self):
#        '''Check the status of the DPT.'''
#        self.check404()
#        if self._thread != None:
#            return
#        elif not self._fetching:
#            t = threading.Thread(target=self._fetch)
#            t.start()
#
#    def _fetch(self):
#        '''Scrapes /g/ for threads and looks for a DPT.'''
#        self._fetching = True
#        try:
#            threads = lib4chan.get_threads(board='g', pages=15)
#            for thread in threads:
#                subj = lib4chan.get_subject(thread)
#                if self._pattern.match(subj):
#                    self._thread = thread
#                    self._url = self.get_url()
#
#                    for chan in self._channels:
#                        self._irc.say(chan, "New DPT: {0}".format(self._url))
#                    break
#        finally:
#            self._fetching = False
#
#    def get_url(self):
#        '''Check for 404, then return either the url or None.'''
#        self.check404()
#        if self._thread == None:
#            return self._url
#        reply = self._thread.find_class("replylink").pop(0)
#        href = reply.attrib['href']
#        return "http://boards.4chan.org/g/" + href
#
#    def check404(self):
#        '''Check if the thread is still alive.'''
#        if self._url == None:
#            return
#        if lib4chan.check404(self._url):
#            self._url = None
#            self._thread = None
#            for chan in self._channels:
#                self._irc.say(chan, "Oh no! The DPT has 404'd!")
