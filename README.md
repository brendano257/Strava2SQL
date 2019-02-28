# Strava2SQL

Getting started with the Strava API can be a hassle if all you wanted was to pull your data and play with it.
Strava2SQL offers a quick and easy way to pull all your activities into a local SQLite database that you can then work with.

Strava2SQL uses only requests and sqlalchemy to download data, but a quick demo uses Pandas for easy data manipulation.

## Basic Use

0) Register an API application with Strava, using 'localhost' for the callback domain (if you don't have or intend to use one).

1) Run initial_auth.py, entering your Strava client ID and client secret from https://www.strava.com/settings/api There are several editable sections in the code. This is only necessary if you would like to retrieve different scopes for access tokens, OR you have more than ~50,000 activities. Search the file for "edit" and read the comments.

2) Run activities_load.py, which will create a SQLite database in the same directory containing all your activities.
  Using DB Browser for SQLite (https://sqlitebrowser.org/) is a good way to get a first glance at your data.

3) Run/view query_test.py to get a printout of your average ride distance (m) by day of week.

