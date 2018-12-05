# Fantasy Football Schedule Analyzer

Do you feel like your team is better than the standings show? It may be because
you had an unlucky schedule this year. This tool lets you see just how big an
impact this year's schedule had on your league.

The script `ScheduleAnalyzer.py` simulates 100,000 hypothetical seasons using
a random schedule each time. The results show how well each team in the league
would do on average, and how much this season's schedule effected them.

## Basic Use

The usage of this script looks like:

```
Usage:
  python3 ScheduleAnalyzer.py arg1 arg2 arg3 [optional args]

  arg1 = ESPN league ID
  arg2 = number of weeks in regular season
  arg3 = number of teams that make playoffs

Optional Args:
  --year XXXX (default=2018)
  --use-csv /path/to/file.csv
```

You must provide an ESPN league ID, the length of your regular season, and
how many teams make the playoffs. If you want to use this tool with a non-ESPN
league see the [Passing a CSV File](#passing-a-csv-file) section. You can optionally
pass a year other than 2018 with `--year XXXX`.

## Example

Here is an example run of the script using a
[public](http://games.espn.com/ffl/standings?leagueId=2090656&seasonId=2018)
12-man league on ESPN.

`python3 ScheduleAnalyzer.py 2090656 13 4`

```
League ID: 2090656
Regular Season Weeks: 1 - 13
Number of Playoff Teams: 4
Year: 2018
 Team  Seed  Avg Seed  Seed Diff  Wins  Avg Wins  Win Diff  Playoff Chance
 DUFU     1       1.1        0.1    12     11.73      0.27           100.0
  TM9     2       3.9        1.9    10       8.6       1.4            70.1
 LINE     3       4.5        1.5     9      8.09      0.91            42.5
 STUD     4       2.9       -1.1     8      9.36     -1.36            89.1
 MADD     5       3.1       -1.9     8      9.27     -1.27            86.5
 HOOS     6       7.9        1.9     6      4.92      1.08             0.9
 JB18     7       8.5        1.5     6      4.73      1.27             0.5
 OTOL     8       6.0       -2.0     5      6.64     -1.64            10.4
   NO     9      10.3        1.3     5      3.49      1.51             0.0
 NICH    10       9.5       -0.5     4      4.09     -0.09             0.0
 BROK    11       9.1       -1.9     3      4.09     -1.09             0.1
  LOL    12      11.1       -0.9     2       3.0      -1.0             0.0
```

Here is a breakdown of the output:

**Team** - Team name abbreviation  
**Seed** - Actual seed going into playoffs  
**Avg Seed** - Average seed over 100,000 simulated schedules  
**Seed Diff** - The difference between the expected and actual seed  
**Wins** - Actual number of regular season wins  
**Avg Wins** - Average number of wins over 100,000 simulated schedules  
**Win Diff** - The difference between the expected and actual number of wins  
**Playoff Chance** - The percentage of simulated schedules that resulted in this
    team making the playoffs  

Let's look at the results from the perspective of the MADD team since they
had a rather unfortunate schedule this year. On average they finish
somewhere around the 3rd seed with 9.27 wins, instead of the 5th seed with 8 wins.
While 1.27 less wins than average doesn't seem like alot, the schedule was also
favorable to TM9 and LINE, enough so that MADD didn't make
the playoffs. The stat that really matters is the last one, **Playoff Chance**.
MADD would've made the playoffs in 86.5% of all possible schedules.

These results also show just how dominant DUFU was, they made the playoffs
in every possible schedule and won 11.73 games on average.

## Passing a CSV File

For non-ESPN leagues, or in cases where the script doesn't work from some
reason, there is an option to pass a csv file with the raw data. See
"sample_data.csv" for an example of what the format should look like. Only
include regular season weeks.

Here is the same example as above, this time using a csv file:

`python3 ScheduleAnalyzer.py 0 13 4 --use-csv sample_data.csv`
