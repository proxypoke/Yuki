# Author: slowpoke <proxypoke at lavabit dot com>
#
# This program is free software under the non-terms
# of the Anti-License. Do whatever the fuck you want.

'''Contains the DPT class.'''

from . import lib4chan

import re
import threading

class DPT(object):
    '''Class that wraps a DPT, storing whether it exists and its url.'''
    def __init__(self, irc, channels):
        # IRC object
        self._irc = irc
        # channels to report to
        self._channels = channels.split(',')
        # thread url
        self._url = None
        # html object
        self._thread = None 
        # fetch lock.
        self._fetching = False
        # subject regex
        self._pattern = re.compile("daily programming thread$", re.I)

    def update(self):
        '''Check the status of the DPT.'''
        self.check404()
        if self._thread != None:
            return
        elif not self._fetching:
            t = threading.Thread(target=self._fetch)
            t.start()

    def _fetch(self):
        '''Scrapes /g/ for threads and looks for a DPT.'''
        self._fetching = True
        try:
            threads = lib4chan.get_threads(board='g', pages=15)
            for thread in threads:
                subj = lib4chan.get_subject(thread)
                if self._pattern.match(subj):
                    self._thread = thread
                    self._url = self.get_url()

                    for chan in self._channels:
                        self._irc.say(chan, "New DPT: {0}".format(self._url))
                    break
        finally:
            self._fetching = False

    def get_url(self):
        '''Check for 404, then return either the url or None.'''
        self.check404()
        if self._thread == None:
            return self._url
        reply = self._thread.find_class("replylink").pop(0)
        href = reply.attrib['href']
        return "http://boards.4chan.org/g/" + href

    def check404(self):
        '''Check if the thread is still alive.'''
        if self._url == None:
            return
        if lib4chan.check404(self._url):
            self._url = None
            self._thread = None
            for chan in self._channels:
                self._irc.say(chan, "Oh no! The DPT has 404'd!")
