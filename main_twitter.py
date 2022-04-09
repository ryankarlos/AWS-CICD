
def handler(event, context):
    from tweets_api import tweepy_search_api, MyStreamListener
    from secrets import get_secrets
    import itertools
    from tweepy import StreamRule

    # Create a Secrets Manager client
    response = get_secrets(mode='local')
    api_keys = list(itertools.islice(response.values(), 4))

    if event['delivery'] == "realtime":
        print('Filtering and streaming realtime Tweets with Twitter Streaming API v1.1: \n')
        stream = MyStreamListener(event,*api_keys)
        stream.filter(track=[event.get('keyword')])

    elif event['delivery'] == 'search':
        print('Starting search stream using tweepy Twitter API v1.1 Client: \n')

        tweepy_search_api(event, *api_keys)
    else:
        raise ValueError(f"'Delivery value in event payload must be either 'search' or 'realtime '.... "
                         f"you passed {event['delivery']}.")
#
#
# if __name__ == "__main__":
#
#     import line_profiler
#     import atexit
#
#     profile = line_profiler.LineProfiler()
#     # prints this just before exiting script
#     atexit.register(profile.print_stats)
#
#     @profile
#     def profiled_function():
#         from secrets import get_secrets
#         from tweets_api import MyStreamListener
#         from tweets_api import tweepy_search_api
#
#     profiled_function()
#       # for realtime - may need to use a trending topic otherwise will have to wait a while to get anything
#     event = {
#       "keyword": "machine learning",
#       "delivery": "search",
#       'duration': 15
#     }
#     context = {}
#     handler(event, context)
#
#
