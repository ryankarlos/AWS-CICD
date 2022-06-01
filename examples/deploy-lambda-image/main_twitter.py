def handler(event, context):
    from tweets_api import tweepy_search_api
    from secrets import get_secrets
    import itertools
    import boto3
    import json
    if isinstance(event, str):
        params = json.loads(event)["CodePipeline.job"]["data"]["actionConfiguration"][
            "configuration"
        ]["UserParameters"]
    else:
        params = event.copy()
    print(params)

    code_pipeline = boto3.client("codepipeline")
    response = get_secrets(mode="aws")
    api_keys = list(itertools.islice(response.values(), 4))
    print(f"Event:{event}")
    print("Searching and delivering Tweets with Tweepy API: \n")
    # special parsing strategy for event from code pipeline as structure is nested differently
    # and of str type so need to convert to dict and parse data key
    # Executing from local_run.py or passing in event for testing lambda function
    # invocation via console - event passed to handler is already of dict type
    try:
        tweepy_search_api(params, *api_keys)
        if params["mode"] == "cloud":
            job_id = event["CodePipeline.job"]["id"]
            code_pipeline.put_job_success_result(jobId=job_id)
    except Exception as e:
        print(str(e))
        if params["mode"] == "cloud":
            job_id = event["CodePipeline.job"]["id"]
            code_pipeline.put_job_failure_result(
                jobId=job_id, failureDetails={"message": str(e), "type": "JobFailed"}
            )
        raise
