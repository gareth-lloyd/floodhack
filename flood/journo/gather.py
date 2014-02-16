import requests, json, tweepy
from datasift import client
from django.contrib.gis.geos import Point
from django.conf import settings

from areas.models import Area
from journo.models import Status

STREAM = '2d614a558ab6b0b84fd1e4aab11a9d2b'

UN = 'godawful'
AK = 'a08da47984e549320122e69e29d3abe3'
DS = 'https://api.datasift.com/v1/stream'
BOT_NAME = "@floodnewsbot"

CSDL = """
interaction.type contains "twitter"
and twitter.user.geo_enabled == 1
and interaction.sample > 0.005
and interaction.geo geo_polygon "49.965360000000004,-5.58105:50.76426000000001,1.2304700000000002:52.82932,2.02148:55.973800000000004,-1.9335900000000001:54.826010000000004,-5.53711"
"""

def _ds():
    ds = client.Client(UN, AK)

    @ds.on_delete
    def on_delete(interaction):
        pass

    @ds.on_open
    def on_open():
        print 'Streaming ready, can start subscribing'
        stream = ds.compile(CSDL)['hash']

        @ds.subscribe(stream)
        def subscribe_to_hash(msg):
            try:
                print msg['interaction'].get('content')
                _consume(msg)
            except Exception, e:
                print e


    @ds.on_closed
    def on_close(wasClean, code, reason):
        print 'Streaming connection closed'

    @ds.on_ds_message
    def on_ds_message(msg):
        print 'DS Message %s' % msg

    #must start stream subscriber
    ds.start_stream_subscriber()
    return client


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


def get_datasift_latest(high_id):
    response = requests.get(
        DS, params={'username': UN, 'api_key': AK, 'hash': STREAM})
    stream = json.loads(response.content)['stream']

    print "got {n} tweets".format(n=len(stream))
    map(_consume, stream)


def _consume(chunk):
    if 'author' not in chunk['interaction']:
        return
    attrs = _attrs(chunk)
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
        if "@godawful" in status.text.lower():
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

