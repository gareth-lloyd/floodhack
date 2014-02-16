import requests, datasift, json
from journo.models import Status
from django.contrib.gis.geos import Point

STREAM = '2d614a558ab6b0b84fd1e4aab11a9d2b'

UN = 'godawful'
AK = 'a08da47984e549320122e69e29d3abe3'
DS = 'https://api.datasift.com/v1/stream'
BOT_NAME = "@floodbot"


def _ds():
    return datasift.User(UN, AK)

def _from_id():
    Status.objects.all().order_by('-created_date')[0].ds_id

def _date(date_str):
    from dateutil import parser
    return parser.parse(date_str)

def _location(chunk):
    geo = chunk['interaction'].get('geo', {})
    if geo:
        return Point(geo['latitude'], geo['longitude'])
    return None

def _is_reply_to_bot(chunk):
    return chunk['interaction'].get('content', 'None').startswith(BOT_NAME)

def _attrs(chunk):
    return {
        'ds_id': chunk['interaction']['id'],
        'tweet_id': chunk['twitter']['id'],
        'uid': str(chunk['interaction']['author']['id']),
        'name': str(chunk['interaction']['author']['name']),
        'username': str(chunk['interaction']['author']['username']),
        'avatar': chunk['interaction']['author']['avatar'],
        'created_date': _date(chunk['interaction']['created_at']),
        'content': chunk['interaction'].get('content', 'None'),
        'location': _location(chunk),
        'reply_to_bot': _is_reply_to_bot(chunk),
    }

def get_latest(high_id):
    response = requests.get(
        DS, params={'username': UN, 'api_key': AK, 'hash': STREAM})
    stream = json.loads(response.content)['stream']
    for chunk in stream:
        attrs = _attrs(chunk)
        try:
            Status.objects.get(ds_id=attrs['ds_id'])
        except Status.DoesNotExist:
            Status.objects.create(**attrs)



