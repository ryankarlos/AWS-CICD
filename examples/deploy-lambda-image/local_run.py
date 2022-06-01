import line_profiler
import atexit
from main_twitter import handler
import click
import json


def profiled_function():
    from secrets import get_secrets
    from tweets_api import MyStreamListener
    from tweets_api import tweepy_search_api


@click.command()
@click.argument("keyword", type=click.STRING)
@click.option(
    "--duration",
    default=15,
    type=click.INT,
    help="How long (secs) to let stream run before disconnecting",
)
@click.option(
    "--mode",
    default="local",
    type=click.STRING,
    help="Whether to run in 'local' mode or in 'cloud' with codepipeline",
)
@click.option(
    "--test_import_speeds",
    default=False,
    type=click.BOOL,
    help="Uses line profiler to test speed of " "imports of custom util functions",
)
def main(keyword, duration, mode, test_import_speeds):
    """
    function for checking/testing tweepy streamingapi locally before deploying as lambda image container
    If test import speed option is set as True, the import stats will be reported before the script ends
    """

    if test_import_speeds:
        profile = line_profiler.LineProfiler()
        atexit.register(profile.print_stats)
        import_speeds = profile(profiled_function)
        import_speeds()

    event = {"keyword": keyword, "duration": duration, "mode": mode}

    context = {}
    handler(event, context)


if __name__ == "__main__":
    main()
