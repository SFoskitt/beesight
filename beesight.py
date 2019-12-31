# mine
import ConfigParser
import calendar
import datetime
import os
import requests
import ssl
import simplejson
import urllib
import urllib2

CONFIG_FILE_NAME = 'config.ini'
INSIGHT_SECTION = 'insight'
BEEMINDER_SECTION = 'beeminder'

INSIGHT_LOGIN_URL = "https://profile.insighttimer.com/profile_signin/request"
INSIGHT_CSV_URL = "https://profile.insighttimer.com/sessions/export"

BEE_BASE_URL = "https://www.beeminder.com/api/v1/"
BEE_GET_DATAPOINTS_URL = BEE_BASE_URL  + "users/%s/goals/%s/datapoints.json?auth_token=%s"
BEE_POST_DATAPOINTS_URL = BEE_GET_DATAPOINTS_URL + "&timestamp=%s&value=%s&comment=%s&requestid=%s"

def get_insight_data():
    # config = ConfigParser.RawConfigParser()
    # config.read(CONFIG_FILE_NAME)

    # username = config.get(INSIGHT_SECTION, "INSIGHT_USERNAME")
    # password = config.get(INSIGHT_SECTION, "INSIGHT_PASSWORD")

    username = os.environ["INSIGHT_USERNAME"]
    password = os.environ["INSIGHT_PASSWORD"]

    values = {'user_session[email]' : username,
              'user_session[password]' : password }
    login_data = urllib.urlencode(values)

    # Start a session so we can have persistent cookies
    session = requests.session()
    r = session.post(INSIGHT_LOGIN_URL, data=login_data)
    r = session.get(INSIGHT_CSV_URL)
    arr = r.text.split('\n')
    return arr

def post_beeminder_entry(entry):
    # config = ConfigParser.RawConfigParser()
    # config.read(CONFIG_FILE_NAME)

    # username = config.get(BEEMINDER_SECTION, "BEEMINDER_USERNAME")
    # auth_token = config.get(BEEMINDER_SECTION, "BEEMINDER_AUTH_TOKEN")
    # goal_name = config.get(BEEMINDER_SECTION, "BEEMINDER_GOAL_NAME")

    username = os.environ["BEEMINDER_USERNAME"]
    auth_token = os.environ["BEEMINDER_AUTH_TOKEN"]
    goal_name = os.environ["BEEMINDER_GOAL_NAME"]

    session = requests.session()
    full_url = BEE_POST_DATAPOINTS_URL % (username, goal_name, auth_token, entry["timestamp"], entry["value"], entry["comment"], entry["requestid"])
    print "full_url %s" % full_url

    r = session.post(full_url)
    print "Posted entry: %s" % r.text

def get_beeminder():
    # config = ConfigParser.RawConfigParser()
    # config.read(CONFIG_FILE_NAME)

    # username = config.get(BEEMINDER_SECTION, "BEEMINDER_USERNAME")
    # auth_token = config.get(BEEMINDER_SECTION, "BEEMINDER_AUTH_TOKEN")
    # goal_name = config.get(BEEMINDER_SECTION, "BEEMINDER_GOAL_NAME")
    username = os.environ["BEEMINDER_USERNAME"]
    auth_token = os.environ["BEEMINDER_AUTH_TOKEN"]
    goal_name = os.environ["BEEMINDER_GOAL_NAME"]

    bee_data_url = BEE_GET_DATAPOINTS_URL % (username, goal_name, auth_token)

    context = ssl._create_unverified_context()
    response = urllib2.urlopen(bee_data_url, context=context)
    the_page = response.read()
    return the_page

def beeminder_to_one_per_timestamp(beeminder_output):
    bm = simplejson.loads(beeminder_output)

    s = {}

    # skip first two header lines
    for entry in bm:
        ts = entry['timestamp']

        if not ts in s:
            s[ts] = 1

    return s.keys()

def csv_to_one_per_timestamp(csv_lines):
    s = {}

    # skip first two header lines
    for l in csv_lines[2:]:
        if l:
            datetime_part = l.split(",")[0]
            date_part = datetime_part.split(" ")[0]
            time_part = datetime_part.split(" ")[1]

            date_parts = date_part.split("/")
            if len(date_parts) == 3:
                m, d, y = map(int, date_parts)
                dt = datetime.date(y, m, d)

            time_parts = time_part.split(":")
            if len(time_parts) == 3:
                hour, min, sec = map(int, time_parts)
                test = datetime.datetime(y, m, d, hour, min, sec)
                ts = calendar.timegm(test.utctimetuple())

                if not ts in s:
                    s[ts] = 0

    return s.keys()

if __name__ == "__main__":
    # get dates of days meditated, from insight
    insight_dates = csv_to_one_per_timestamp(get_insight_data())
    print "%s days meditated according to insighttimer.com" % len(insight_dates)

    # get dates of days meditated, from beeminder
    beeminder_dates = beeminder_to_one_per_timestamp(get_beeminder())
    print "%s datapoints in beeminder" % len(beeminder_dates)

    # get dates which beeminder doesn't know about yet
    bee_sorted = sorted(set(beeminder_dates))
    insight_sorted = sorted(set(insight_dates))
    inter = list(set(insight_dates) - set(beeminder_dates))
    new_data = sorted(list(set(insight_dates) - set(beeminder_dates)))
    print "new dates len: %s" % len(new_data)

    for ts in new_data:
      requestid = "insighttimer_%s" % ts
      entry = {"timestamp": ts, "requestid": requestid, "value":1, "comment":"Heroku to InsightsTimer to Beeminder"}
      print "entry values %s" % entry
      post_beeminder_entry(entry)
