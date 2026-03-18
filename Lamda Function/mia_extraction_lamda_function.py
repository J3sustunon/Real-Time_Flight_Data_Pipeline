import json
import boto3
import urllib3
import datetime

FIREHOSE_NAME = 'PUT-S3-EEHVY'
RAPIDAPI_KEY = '6eb816bda6mshb7ae3df406631d0p10262ajsna31719977fa0'

def lambda_handler(event, context):
    
    http = urllib3.PoolManager()

    now = datetime.datetime.utcnow()
    from_time = (now - datetime.timedelta(hours=12)).strftime('%Y-%m-%dT%H:00')
    to_time = now.strftime('%Y-%m-%dT%H:00')

    r = http.request(
        "GET",
        f"https://aerodatabox.p.rapidapi.com/flights/airports/icao/KMIA/{from_time}/{to_time}",
        headers={
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
        },
        fields={
            "direction": "Arrival",
            "withCodeshared": "false",
            "withCancelled": "true",
            "withCargo": "false",
            "withPrivate": "false",
            "withLocation": "false"
        }
    )

    
    r_dict = json.loads(r.data.decode(encoding='utf-8', errors='strict'))

    if 'arrivals' not in r_dict or len(r_dict['arrivals']) == 0:
        return {"status": "no flights in this window"}

    # append to list records_to_push
    # each record is a new list item
    records_to_push = []
    for i in range(len(r_dict['arrivals'])):
        processed_dict = {}
        movement = r_dict['arrivals'][i].get('movement', {})
        processed_dict['row_ts']            = str(datetime.datetime.now())
        processed_dict['flight_n']          = r_dict['arrivals'][i].get('number', 'N/A')
        processed_dict['airline_name']      = r_dict['arrivals'][i].get('airline', {}).get('name', 'N/A')
        processed_dict['arriving_from']     = movement.get('airport', {}).get('name', 'N/A')
        processed_dict['arriving_apt_code'] = movement.get('airport', {}).get('iata', 'N/A')
        processed_dict['actual_arrival']    = movement.get('runwayTime', {}).get('utc', 'N/A')
        processed_dict['scheduled_arrival'] = movement.get('scheduledTime', {}).get('utc', 'N/A')
        processed_dict['flight_status']     = r_dict['arrivals'][i].get('status', 'N/A')
        if processed_dict['actual_arrival'] is None:
            processed_dict['actual_arrival'] = 'N/A'

        msg = str(processed_dict) + '\n'
        records_to_push.append({'Data': msg})

    fh = boto3.client('firehose')

    reply = fh.put_record_batch(
        DeliveryStreamName=FIREHOSE_NAME,
        Records=records_to_push
    )

    return reply



