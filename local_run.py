import line_profiler
import atexit
from main_twitter import handler

# for 'realtime' delivery - may need to use a trending topic otherwise will have to wait a while to get anything
event = {
  "keyword": "machine learning",
  "delivery": "search",
  'duration': 15
}
context = {}
handler(event, context)


# for testing import speeds

profile = line_profiler.LineProfiler()
# prints this just before exiting script
atexit.register(profile.print_stats)


@profile
def profiled_function():
    from secrets import get_secrets
    from tweets_api import MyStreamListener
    from tweets_api import tweepy_search_api


profiled_function()


