"""
A bot to post from rss feeds to a given subreddit
Written by /u/SmBe19
"""

import praw
import time
import OAuth2Util
import RSSReader

# ### USER CONFIGURATION ### #

# The bot's useragent. It should contain a short description of what it does and your username. e.g. "RSS Bot by /u/SmBe19"
USERAGENT = ""

# The name of the subreddit to post to. e.g. "funny"
SUBREDDIT = ""

# The time in seconds the bot should sleep until it checks again.
SLEEP = 60*60

# If True, the bot will submit a link even if reddit says it was already submitted. This can be the case if it was submitted in an other subreddit or by an other user, or if the bot failed with keeping track of already submitted articles (shouldn't be the case).
RESUBMIT_ANYWAYS = True

# If True, the bot will post a comment with the description of the article.
POST_DESCRIPTION = True

# The text the bot should post with the description, {0} will be replaced by the description
DESCRIPTION_FORMAT = "Link description:\n\n{0}"

# ### END USER CONFIGURATION ### #

# ### BOT CONFIGURATION ### #
SOURCES_CONFIGFILE = "sources.txt"
DONE_CONFIGFILE = "done.txt"
# ### END BOT CONFIGURATION ### #

try:
	# A file containing data for global constants.
	import bot
	for k in dir(bot):
		if k.upper() in globals():
			globals()[k.upper()] = getattr(bot, k)
except ImportError:
	pass

def read_config_sources():
	sources = []
	try:
		with open(SOURCES_CONFIGFILE, "r") as f:
			for line in f:
				sources.append(line)
	except OSError:
		print(SOURCES_CONFIGFILE, "not found.")
	return sources

def read_config_done():
	done = []
	try:
		with open(DONE_CONFIGFILE, "r") as f:
			for line in f:
				if line.strip():
					done.append(line.strip())
	except OSError:
		print(DONE_CONFIGFILE, "not found.")
	return done

def write_config_done(done):
	with open(DONE_CONFIGFILE, "w") as f:
		for d in done:
			if d:
				f.write(d + "\n")

# main procedure
def run_bot():
	r = praw.Reddit(USERAGENT)
	o = OAuth2Util.OAuth2Util(r)
	o.refresh()
	sub = r.get_subreddit(SUBREDDIT)

	print("Start bot for subreddit", SUBREDDIT)

	done = read_config_done()

	while True:
		try:
			o.refresh()
			sources = read_config_sources()

			print("check sources")
			newArticles = []
			for source in sources:
				newArticles.extend(RSSReader.get_new_articles(source))

			for article in newArticles:
				if article[3] not in done:
					done.append(article[3])
					try:
						submission = sub.submit(article[0], url=article[1], resubmit=RESUBMIT_ANYWAYS)
						if POST_DESCRIPTION and article[2] is not None:
							submission.add_comment(DESCRIPTION_FORMAT.format(article[2]))
					except praw.errors.AlreadySubmitted:
						print("already submitted")
					else:
						print("submit article")

		# Allows the bot to exit on ^C, all other exceptions are ignored
		except KeyboardInterrupt:
			break
		except Exception as e:
			print("Exception", e)

		write_config_done(done)
		print("sleep for", SLEEP, "s")
		time.sleep(SLEEP)

	write_config_done(done)


if __name__ == "__main__":
	if not USERAGENT:
		print("missing useragent")
	elif not SUBREDDIT:
		print("missing subreddit")
	else:
		run_bot()
