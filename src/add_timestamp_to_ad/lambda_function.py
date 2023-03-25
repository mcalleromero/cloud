import time

DAY = 86400  # POSIX day (exact value)


def lambda_handler(event, context):
    response = event
    currdate = int(time.time())
    timestamps = {"timestamp": str(currdate), "expdate": str(currdate + 5 * DAY)}
    extra_info = {"id": f"{currdate}_{event['user']}"}
    response.update(**timestamps, **extra_info)
    return response
