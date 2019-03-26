from core import connect_to_db, Activity, Segment
from datetime import datetime
from pathlib import Path
import pandas as pd
import os

engine, session, Base = connect_to_db('sqlite:///activity_db.sqlite', Path(os.getcwd()) / '..')

# commute_segment_list = ['Climb over Walnut',
#                         "Back to JJ's from Pearl East Cir. (high-five a JJ's sammich hustler for bonus points)",
#                         'Foothills Bridge Climb Southbound',
#                         'Confluence to Walnut Ramp']

commute_segment_list = ['Bear Creek Path from Park East to 36', 'Baseline Church to Broadway on Path',
                        "chancellor's house flyby S", 'Martin Park Climb', 'Totally South']

ct = 0

for segment_name in commute_segment_list:
    results = (session.query(Activity, Segment)
               .filter(Activity.start_date_local.between(datetime(2018,7,1), datetime(2018,12,30)))
               .join(Segment, Activity.strava_id == Segment.activity_id)
               .filter(Segment.name == segment_name)
               .all())

    dates = []
    elapsed_times = []
    for r in results:
        dates.append(r.Activity.start_date_local)
        elapsed_times.append(r.Segment.elapsed_time.seconds)

    df = pd.DataFrame({'date': dates, 'elapsed_time': elapsed_times})
    df['dow'] = df['date'].dt.dayofweek

    dow_grouped = df['elapsed_time'].groupby(df['dow'])

    stats_input = ({'mean': dow_grouped.mean(), 'median': dow_grouped.median(),
                    'stdev': dow_grouped.std(), 'n': dow_grouped.count(),
                    'min': dow_grouped.min(), 'max': dow_grouped.max()})

    stats = pd.DataFrame.from_dict(stats_input, orient='columns')  # [dow_grouped.mean(), dow_grouped.median()]

    stats.rename(index={0:'Monday', 1:'Tuesday', 2: 'Wednesday',
                        3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}, inplace=True)

    if 'Saturday' in stats.index.tolist():
        stats.drop('Saturday', inplace=True)
    if 'Sunday' in stats.index.tolist():
        stats.drop('Sunday', inplace=True)

    import matplotlib.pyplot as plt

    f1 = plt.figure()
    ax = f1.gca()
    ax.bar(stats.index, stats['mean'], width=.5, color='blue')
    # ax.bar(stats.index, stats['median'], width=.5, color='red')
    ax.bar(stats.index, stats['stdev'], width=.5, color='orange')

    ax.tick_params(axis='both', which='major', size=8, width=2, labelsize=15)
    ax.tick_params(axis='x', labelrotation=20)
    [i.set_linewidth(2) for i in ax.spines.values()]
    f1.set_size_inches(11.11, 7.406)
    f1.subplots_adjust(bottom=.10)

    ax.set_ylabel('Elapsed Time (s)', fontsize=20)
    ax.set_title(f'Segment: {segment_name}')
    ax.legend(['Mean', 'StDev'])

    f1.savefig(f'segment_{ct}.png', dpi=150)

    ct += 1



