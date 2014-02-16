import requests, datasift, json, tweepy
from django.contrib.gis.geos import Point
from django.conf import settings

from areas.models import Area
from journo.models import Status

STREAM = '2d614a558ab6b0b84fd1e4aab11a9d2b'

UN = 'godawful'
AK = 'a08da47984e549320122e69e29d3abe3'
DS = 'https://api.datasift.com/v1/stream'
BOT_NAME = "@floodnewsbot"

def _tw():
    auth = tweepy.OAuthHandler(settings.TW_KEY, settings.TW_SECRET)
    auth.set_access_token(settings.TW_ACC, settings.TW_ACC_SEC)
    return tweepy.API(auth_handler=auth)

def _message(at_name):
    return "{at_name} you're tweeting from an area with flood"\
        " warnings. Hope you're OK! Can you send me an update"\
        " or a photo?".format(at_name=at_name)

def request(status):
    tw = _tw()
    at_name = u"@{n}".format(n=status.username)
    message = _message(at_name)
    if len(message) > 140:
        return

    tw.update_status(_message(at_name), status.tweet_id)

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
        'tweet_id': str(chunk['twitter']['id']),
        'uid': str(chunk['interaction'].get('author',{}).get('id', '0')),
        'name': chunk['interaction'].get('author', {}).get('name', {}),
        'username': chunk['interaction']['author']['username'],
        'avatar': chunk['interaction']['author']['avatar'],
        'created_date': _date(chunk['interaction']['created_at']),
        'content': chunk['interaction'].get('content', 'None'),
        'location': _location(chunk),
        'reply_to_bot': _is_reply_to_bot(chunk),
    }

def is_in_flood_area(location):
    if not location:
        return False
    return Area.objects.filter(shape__contains=location).exists()


seen = set()

def get_datasift_latest(high_id):
    response = requests.get(
        DS, params={'username': UN, 'api_key': AK, 'hash': STREAM})
    stream = json.loads(response.content)['stream']

    print "got {n} tweets".format(n=len(stream))
    for chunk in stream:
        if 'author' not in chunk['interaction']:
            continue
        attrs = _attrs(chunk)
        if not attrs['ds_id'] in seen:
            seen.add(attrs['ds_id'])
            print 'new one'

        if Status.objects.filter(tweet_id=attrs['tweet_id']).exists():
            print 'seen before'

        if is_in_flood_area(attrs['location']):
            print 'creating', attrs['content']
            status = Status.objects.create(**attrs)
            if not status.reply_to_bot:
                print 'requesting from', status.username
                request(status)


def get_latest_mentions():
    tw = _tw()
    for status in tw.mentions_timeline():
        if "@godawful" in status.text:
            continue
        elif Status.objects.filter(tweet_id=str(status.id)).exists():
            continue
        else:
            try:
                lat, lng = status.geo['coordinates']
            except:
                lat, lng = None, None
            print 'found mention'
            Status.objects.create(
                ds_id=None,
                tweet_id=str(status.id),
                uid=str(status.user.id),
                name=status.user.name,
                username=status.user.screen_name,
                avatar=status.user.profile_image_url,
                created_date=status.created_at,
                content=status.text,
                location=Point(lat, lng) if bool(lat) else None,
                reply_to_bot=True,
            )

