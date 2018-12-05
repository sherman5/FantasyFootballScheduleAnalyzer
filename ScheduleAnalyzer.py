import sys
if sys.version_info[0] != 3:
    print("Error: this script requires Python 3")
    sys.exit(1)

import requests
import pandas as pd
from collections import defaultdict
from random import shuffle

########################## help and usage information ##########################

help_msg = """
This script provides a way to analyze the effect your particular fantasy
schedule had this year, and shows how well each team would do on average
across all possible schedules.

You must provide a league ID, the length (number of weeks) of your 
regular season, and the number of teams that make the playoffs. You may also
pass the year you want to analyze.

NOTE: if you don't use ESPN there is also an option to pass a csv file with
your league's raw data - see the README on GitHub for more information.

This method works by simulating 100,000 possible seasons with a random schedule
used each time. The output shows the comparison between the actual results of
the league and the expected results of the league. It also calculates how
often each team makes the playoffs. E.g. Playoff Chance = 75.3
means 75.3% of all possible schedules would result with that team
in the playoffs.

You may notice that even when team A has more average wins than team B, team B
has a higher chance of making the playoffs. This happens when team B has the
tiebreaker over team A, so in any schedule where they tie, team B will make it
to the playoffs over team A. The tiebreaker defaults to total points on the
year, so if your league uses somthing else, open an issue on GitHub so that it
can get added.

Note about private leagues: There is a work-around if you cannot access
your league's info since it's private - however, it seems that when querying
the API directly it ignores the public/private status and so the work-around
is not neccesary. If you do see this issue then please report it on GitHub
and the script will be updated with the work-around.

Credit to https://stmorse.github.io/journal/espn-fantasy-python.html
for the code to get information from the ESPN Fantasy API.
"""

usage_msg = """
Usage:
  python3 ScheduleAnalyzer.py arg1 arg2 arg3 [optional args]

  arg1 = ESPN league ID
  arg2 = number of weeks in regular season
  arg3 = number of teams that make playoffs

Optional Args:
  --year XXXX (default=2018)
  --use-csv /path/to/file.csv

For more Information:
  python3 ScheduleAnalyzer.py --help
"""

################################## functions ###################################

# print error message, usage message, then exit
def exit_with_error(msg):
    print("Error: " + msg)
    print(usage_msg)
    sys.exit(1)

# get data from espn, cleanup and return
def get_espn_data(league_id, year):
    # verify league id
    try:
        r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard',
            params={'leagueId': league_id, 'seasonId': year, 'matchupPeriodId': 1})
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        print("This is probably an issue with the league ID or the year")
        sys.exit(1)

    # download raw data
    league_summary = {}
    for week in all_weeks:
        r = requests.get('http://games.espn.com/ffl/api/v2/scoreboard',
            params={'leagueId': league_id, 'seasonId': year, 'matchupPeriodId': week})
        league_summary[week] = r.json()

    # check if final week has happened yet
    final_week_summ = league_summary[final_week]['scoreboard']['matchups']
    final_week_total_score = 0
    for match in final_week_summ:
        final_week_total_score += match['teams'][0]['score']
        final_week_total_score += match['teams'][1]['score']
    if final_week_total_score == 0:
        exit_with_error("week " + str(final_week) + " has not been played yet")

    # get weekly points for all weeks, all teams
    points = defaultdict(list)
    for week in league_summary:
        temp = league_summary[week]['scoreboard']['matchups']
        for match in temp:
            points[match['teams'][0]['team']['teamAbbrev']].append(match['teams'][0]['score'])
            points[match['teams'][1]['team']['teamAbbrev']].append(match['teams'][1]['score'])
    teams = list(points.keys())

    # get actual number of wins
    wins = dict.fromkeys(teams, 0)
    for week in league_summary:
        temp = league_summary[week]['scoreboard']['matchups']
        for match in temp:
            if match['teams'][0]['score'] > match['teams'][1]['score']:
                wins[match['teams'][0]['team']['teamAbbrev']] += 1
            elif match['teams'][1]['score'] > match['teams'][0]['score']:
                wins[match['teams'][1]['team']['teamAbbrev']] += 1

    return teams, points, wins

# read data from local csv file
def get_csv_data(csv_path, n_weeks):
    data = pd.read_csv(csv_path)
    if len(data.columns) - 2 != n_weeks:
        exit_with_error("Number of regular season weeks does not match csv")
    teams = list(data.iloc[:,0:1].values.flatten())
    wins = dict(zip(teams, list(data.iloc[:,1:2].values.flatten())))
    points = defaultdict(list)
    for i, name in enumerate(teams):
        points[name] = data.iloc[i,2:].values
   
    return teams, points, wins

# parse the input data and return:
# teams (list), points (dict), wins (dict)
def get_data(league_id, year, use_csv, csv_path, n_weeks):
    if use_csv:
        return get_csv_data(csv_path, n_weeks)
    else:
        return get_espn_data(league_id, year)

# used to advance matchups week to week
# assumed here that home_teams[i] will play away_teams[i]
def advance_round_robin(home_teams, away_teams):
    temp = away_teams[0]

    for i in range(len(away_teams)-1):
        away_teams[i] = away_teams[i+1]
    away_teams[len(away_teams)-1] = home_teams[len(home_teams)-1]

    for i in range(len(away_teams)-1, 1, -1):
        home_teams[i] = home_teams[i-1]
    home_teams[1] = temp

    return home_teams, away_teams

############################# command line parsing #############################

# print help message if requested
if len(sys.argv) > 1 and sys.argv[1] == "--help":
    print(usage_msg)
    print(help_msg)
    sys.exit(1)

# make sure enough arguments are provided
if len(sys.argv) < 4:
    exit_with_error("not enough arguments provided")

# get required command line arguments
league_id = sys.argv[1]
final_week = int(sys.argv[2])
n_playoff_teams = int(sys.argv[3])
all_weeks = range(1,final_week+1)

# these are optional arguments
year = "2018"
use_csv = False
csv_path = ""

# get optional arguments from command line
for i in range(4, len(sys.argv) - 1, 2):
    if sys.argv[i] == "--year":
        year = sys.argv[i+1]
    elif sys.argv[i] == "--use-csv":
        use_csv = True
        csv_path = sys.argv[i+1]
        print("Using CSV file and ignoring league ID and year")
    else:
        exit_with_error("invalid optional argument")

# print info about this run
print("League ID: " + league_id)
print("Regular Season Weeks: 1 - " + str(final_week))
print("Number of Playoff Teams: " + str(n_playoff_teams))
print("Year: " + year)

################################## main script #################################

# get raw points data
teams, points, actual_wins = get_data(league_id, year, use_csv, csv_path, final_week)

# get total points
total_points = dict.fromkeys(teams, 0)
for team in teams:
    total_points[team] = sum(points[team])

# get actual seed, break ties with total points
actual_seed = []
for team in teams:
    actual_seed.append([team, actual_wins[team], total_points[team]])
actual_seed.sort(key=lambda tup: (tup[1], tup[2]), reverse=True)

# simulate season with random schedules
n_seasons = 100000
playoff_appearances = dict.fromkeys(teams, 0)
expected_wins = dict.fromkeys(teams, 0)
expected_seed = dict.fromkeys(teams, 0)
n_teams = len(teams)
midpoint = int(n_teams / 2)

for n in range(n_seasons):
    # set up this season's schedule
    shuffle(teams)
    home_teams = teams[0:midpoint]
    away_teams = teams[midpoint:n_teams]

    # simulate regular season
    season_wins = dict.fromkeys(teams, 0)
    for week in all_weeks:
        for home, away in zip(home_teams, away_teams):
            if points[home][week-1] > points[away][week-1]:
                season_wins[home] += 1
            elif points[home][week-1] < points[away][week-1]:
                season_wins[away] += 1
            else: # tie
                season_wins[home] += 0.5
                season_wins[away] += 0.5
        home_teams, away_teams = advance_round_robin(home_teams, away_teams)

    # sort by most wins, break ties with total points
    season_stats = []
    for team in teams:
        season_stats.append([team, season_wins[team], total_points[team]])
    season_stats.sort(key=lambda tup: (tup[1], tup[2]), reverse=True)

    # record the seed, wins, and whether or not a team made the playoffs
    for i, tup in enumerate(season_stats):
        expected_seed[tup[0]] += i + 1
        expected_wins[tup[0]] += tup[1]
        if i < n_playoff_teams:
            playoff_appearances[tup[0]] += 1

# get average stats
sos = dict.fromkeys(teams, 0)
for i in expected_seed:
    expected_seed[i] = round(expected_seed[i] / n_seasons, 1)
    expected_wins[i] = round(expected_wins[i] / n_seasons, 2)
    sos[i] = round(actual_wins[i] - expected_wins[i], 2)
    playoff_appearances[i] = round(playoff_appearances[i] * 100 / n_seasons, 1)

# create tuple of all season info
season_summary = []
for i, tup in enumerate(actual_seed):
    name = tup[0]
    season_summary.append([
        name.upper(),                                       # 0 - team name
        i+1,                                                # 1 - actual seed
        expected_seed[name],                                # 2 - average seed
        round(expected_seed[name] - i-1, 1),                # 3 - seed diff
        actual_wins[name],                                  # 4 - actual wins
        expected_wins[name],                                # 5 - average wins
        round(actual_wins[name] - expected_wins[name], 2),  # 6 - win diff
        playoff_appearances[name]])                         # 7 - playoff chance

# sort by a condition
season_summary.sort(key=lambda tup: tup[1], reverse=False)

def formatted_print(x):
    print('{:>5}'.format(str(x[0])) +
          '{:>6}'.format(str(x[1])) + 
         '{:>10}'.format(str(x[2])) +
         '{:>11}'.format(str(x[3])) +
          '{:>6}'.format(str(x[4])) + 
         '{:>10}'.format(str(x[5])) +
         '{:>10}'.format(str(x[6])) + 
         '{:>16}'.format(str(x[7])))

# print season summary info
formatted_print(["Team", "Seed", "Avg Seed", "Seed Diff", "Wins", "Avg Wins",
    "Win Diff", "Playoff Chance"])
for team_summ in season_summary:
    formatted_print(team_summ)

