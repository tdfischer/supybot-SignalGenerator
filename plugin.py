###
# Copyright (c) 2012-2014, Torrie Fischer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class SQLiteSignalDB(object):
    def __init__(self, filename)
        self.dbs = ircutils.IrcDict()
        self.filename = filename

    def close(self):
        for db in self.dbs.values():
            db.commit()
            db.close()

    def _getDb(self, channel):
        if channel not in self.dbs:
            filename = plugins.makeChannelFilename(self.filename, channel)
            self.dbs[channel] = sqlite3.connect(filename)
            c = self.dbs[channel].execute("PRAGMA user_version")
            version = c.fetchone()[0]
            self._upgradeDb(self.dbs[channel], version)
        return self.dbs[channel]

    def _upgradeDb(self, db, current):
        if (current == 0):
            current = 1
            db.execute("CREATE TABLE phrases (phrase TEXT KEY)")
        db.execute("PRAGMA user_version=%i"%current)
        db.commit()

    def addPhrase(self, channel, phrase):
        c = self._getDb(channel).cursor()
        c.execute("INSERT INTO phrases (phrase) VALUES (?)", phrase)
        self._getDb(channel).commit()

    def hasMatch(self, channel, phrase):
        c = self._getDb(channel).cursor()
        c.execute("SELECT phrase FROM phrases WHERE phrase = ?", phrase)
        if c.fetchone() is None:
            return False
        return True

SignalDB = plugins.DB('SignalGenerator', {'sqlite': SQLiteSignalDB})


class SignalGenerator(callbacks.Plugin):
    """Add the help for "@plugin help SignalGenerator" here
    This should describe *how* to use this plugin."""
    def __init__(self, irc):
        self.__parent = super(SignalGenerator, self)
        super(SignalGenerator, self).__init__(irc)
        self.db = SignalDB()

    def die(self):
        self.__parent.die()
        self.db.close()

    def handleNoiseEmitter(self, irc, msg):
        channel = plugins.getChannel(msg.args[0])
        useKick = self.registryValue('useKicks', channel)
        msg = ""
        if ircmsgs.isAction(msg):
            msg = ircmsgs.unAction(msg)
        else:
            msg = msg.args[1]

        if self.db.hasMatch(channel, msg):
            if useKick:
                irc.queueMsg(ircmsgs.kick(channel, msg.nick, 'noise'))
                banmask = ircutils.banmask(
                irc.queueMsg(ircmsgs.ban(channel, banmask))

    def isNoisy(self, msg):
        channel = plugins.getChannel(msg.args[0])

    def doPrivmsg(self, irc, msg):
        if (irc.isChannel(msg.args[0])):
            channel = plugins.getChannel(msg.args[0])


Class = SignalGenerator


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
