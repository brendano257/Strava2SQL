# Strava2SQL

Getting started with the Strava API can be a hassle if all you wanted was to pull your data and play with it.
Strava2SQL offers a quick and easy way to pull all your activities into a local SQLite database that you can then work with.

## Basic Use

0) Register an API application with Strava, using 'localhost' for the callback domain (if you don't have or intend to use one).

1) Run initial_auth.py, entering your Strava client ID and client secret from https://www.strava.com/settings/api

2) Run activities_load.py, which will create a SQLite database in the same directory containing all your activities.

3) Run query_test.py to get a printout of your average ride distance (m) by day of week.

