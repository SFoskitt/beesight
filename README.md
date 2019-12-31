beesight.py
-------------
This is a small script which retrieves meditation data from insighttimer.com and posts the data points to your beeminder goal, so that you can easily track how often you're meditating.

This fork of davecahill/beesight.py will post one datapoint for each unique timestamp in InsightTimer data which is not in Beeminder data.

It is intended to be run on a cron, picking up new datapoints and posting them to beeminder.

The master branch of this fork is running on a Heroku worker dyno with Heroku Scheduler (free add-on) twice a day.  Heroku config variables must be set up with this config.

The `run-local` branch of this fork can be run in a terminal with `python beesight.py`.  Local config.ini must contain config variables.

Usage
---------

Copy default_config.ini to config.ini and fill in your insighttimer.com and beeminder credentials.

Your beeminder auth token can be found at this URL when logged in:
https://www.beeminder.com/api/v1/auth_token.json

To run:
```
python beesight.py
```

If you see the message "ImportError: no module named requests", you'll need to install the python [requests](http://docs.python-requests.org/en/master/) library by running:
```
pip install requests
```
If you hit any issues installing requests, further instructions are here:
http://docs.python-requests.org/en/master/user/install/

Notes
------
In the davecahill/beesight original repo, beesight.py currently subtracts one from the dates it gets from beeminder,
because beeminder returns JST (Japanese Standard Time) 01:00 on (correct_day + 1)
in my timezone. If you're in another timezone, this may cause your dates
to be off by one. 

In this fork of the repo, there is no timezone mathematics involved.  All timestamps are in UTC.

