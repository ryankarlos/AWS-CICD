def handler(event, context):
    from tweets_api import tweepy_search_api
    from secrets import get_secrets
    import itertools
    import boto3
    import json

    print(f"Event payload type: {type(event)}")
    print(f"Event:{event}")
    if event.get("CodePipeline.job") is not None:
        mode = "cloud"
    else:
        mode = "local"
    print(f"Mode: {mode}")
    # special parsing strategy for event from code pipeline as structure is nested differently -
    # parameter stored in UserParameters key as str. So need extra step to convert this to dict
    if mode == "cloud":
        data = event["CodePipeline.job"]["data"]["actionConfiguration"][
            "configuration"
        ]["UserParameters"]
        params = json.loads(data)
        job_id = event["CodePipeline.job"]["id"]
        print(f"Params:{params}, JobID: {job_id}")
    # Executing from local_run.py or passing in event for testing lambda function invocation via console
    elif mode == "local":
        params = event.copy()
        print(f"Params:{params}")
    code_pipeline = boto3.client("codepipeline")
    response = get_secrets(mode="aws")
    api_keys = list(itertools.islice(response.values(), 4))
    print("Searching and delivering Tweets with Tweepy API: \n")

    try:
        tweepy_search_api(params, *api_keys)
        if mode == "cloud":
            code_pipeline.put_job_success_result(jobId=job_id)
    except Exception as e:
        print(f"Exception:{str(e)}")
        if mode == "cloud":
            code_pipeline.put_job_failure_result(
                jobId=job_id, failureDetails={"message": str(e), "type": "JobFailed"}
            )
        raise
