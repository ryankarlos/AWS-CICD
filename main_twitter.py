
def handler(event, context):
    from tweets_api import tweepy_search_api, MyStreamListener
    from secrets import get_secrets
    import itertools

    # Create a Secrets Manager client
    response = get_secrets(mode='local')

    if event['delivery'] == "stream":
        print('Filtering and streaming realtime Tweets with Twitter API v2: \n')
        stream = MyStreamListener(event,response['BearerToken'])
        stream.filter(track=event.get('keyword'))

    elif event['delivery'] == 'search':
        print('Starting search stream using tweepy Twitter API v1.1 Client: \n')
        api_keys = list(itertools.islice(response.values(), 4))
        tweepy_search_api(event, *api_keys)
    else:
        raise ValueError(f"'Delivery value in event payload must be either 'search' or 'stream'.... "
                         f"you passed {event['delivery']}.")


if __name__ == "__main__":

    import line_profiler
    import atexit

    profile = line_profiler.LineProfiler()
    # prints this just before exiting script
    atexit.register(profile.print_stats)

    @profile
    def profiled_function():
        from secrets import get_secrets
        from tweets_api import MyStreamListener
        from tweets_api import tweepy_search_api

    profiled_function()

    event = {
      "keyword": "machine learning",
      "delivery": "search",
      'duration': 15
    }
    context = {}
    handler(event, context)