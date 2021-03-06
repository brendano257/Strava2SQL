import os
import json
import datetime as dt
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Interval, Boolean, ForeignKey

activity_var_list = (['resource_state', 'athlete', 'name', 'distance',
                      'total_elevation_gain', 'type', 'workout_type', 'strava_id', 'external_id', 'upload_id',
                      'timezone', 'utc_offset', 'start_latlng', 'end_latlng',
                      'location_city', 'location_state', 'location_country', 'start_latitude', 'start_longitude',
                      'achievement_count', 'kudos_count', 'comment_count', 'athlete_count', 'photo_count', 'map',
                      'trainer', 'commute', 'manual', 'private', 'visibility', 'flagged', 'gear_id',
                      'from_accepted_tag', 'average_speed', 'max_speed', 'average_temp', 'average_watts', 'kilojoules',
                      'device_watts', 'has_heartrate', 'heartrate_opt_out', 'display_hide_heartrate_option',
                      'elev_high', 'elev_low', 'pr_count', 'total_photo_count', 'has_kudoed'])

activity_edit_fields = ['athlete_id']
activity_date_fields = ['start_date', 'start_date_local']
activity_timedelta_fields = ['moving_time', 'elapsed_time']

effort_var_list = ['resource_state', 'name', 'elapsed_time', 'moving_time'
                   'start_date', 'start_date_local', 'distance', 'start_index', 'end_index', 'device_watts',
                   'average_watts', 'kom_rank', 'pr_rank', 'achievements', 'hidden']

effort_edit_fields = ['effort_id', 'activity_id', 'athlete_id']
effort_datetime_fields = ['start_date', 'start_date_local']
effort_timedelta_fields = ['elapsed_time', 'moving_time']

segment_var_list = ['activity_type', 'average_grade', 'maximum_grade', 'elevation_high', 'elevation_low', 'start_latlng',
                'end_latlng', 'climb_category', 'city', 'state', 'country', 'private', 'hazardous', 'starred']

segment_edit_list = ['segment_id', 'segment_resource_state', 'segment_name', 'segment_distance']


class JDict(TypeDecorator):
    """
    Serializes a dictionary for SQLAlchemy storage.
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


MutableDict.associate_with(JDict)


class JList(TypeDecorator):
    """
    Serializes a list for SQLAlchemy storage.
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        value = json.loads(value)
        return value


MutableList.associate_with(JList)

Base = declarative_base()


class Athlete(Base):
    """Currently un-used"""
    __tablename__ = 'athletes'

    id = Column(Integer, primary_key=True)
    strava_id = Column(Integer)
    resource_state = Column(Integer)

    activity_con = relationship('Activity')
    segment_con = relationship('Segment')

    def __init__(self, id, resource_state):
        self.strava_id = id
        self.resource_state = resource_state

class Segment(Base):
    """
    A class containing all that's returned when parsing efforts from 'include_all_efforts:'true' from an activity response.

    Efforts are a segment run, but carry segment information in a dict. These are separated within the segment class,
    and share some information between both.
    """

    __tablename__ = 'segments'

    ### EFFORT Variables
    id = Column(Integer, primary_key=True)
    effort_id = Column(Integer)  # EDITED
    resource_state = Column(Integer)
    name = Column(String)
    activity_id = Column(Integer, ForeignKey('activities.id'))  # EDITED
    athlete_id = Column(Integer, ForeignKey('athletes.strava_id'))  # EDITED
    elapsed_time = Column(Interval)
    moving_time = Column(Interval)
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    distance = Column(Float)
    start_index = Column(Integer)
    end_index = Column(Integer)
    device_watts = Column(Boolean)
    average_watts = Column(Float)
    kom_rank = Column(Integer)
    pr_rank = Column(Integer)
    achievements = Column(MutableList.as_mutable(JList))
    hidden = Column(Boolean)

    ### SEGMENT Variables
    segment_id = Column(Integer)  # EDITED
    segment_resource_state = Column(Integer)  # EDITED
    segment_name = Column(String)  # EDITED
    activity_type = Column(String)
    segment_distance = Column(Float)  # EDITED
    average_grade = Column(Float)
    maximum_grade = Column(Float)
    elevation_high = Column(Float)
    elevation_low = Column(Float)
    start_latlng = Column(MutableList.as_mutable(JList))
    end_latlng = Column(MutableList.as_mutable(JList))
    climb_category = Column(Integer)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    private = Column(Boolean)
    hazardous = Column(Boolean)
    starred = Column(Boolean)

    def __init__(self, segment_dict):
        for item in effort_var_list:
            setattr(self, item, segment_dict.get(item, None))

        for item in effort_datetime_fields:
            val = datetime.strptime(segment_dict.get(item, None), '%Y-%m-%dT%H:%M:%SZ')
            setattr(self, item, val)

        for item in effort_timedelta_fields:
            val = dt.timedelta(seconds=segment_dict.get(item, None))
            setattr(self, item, val)

        self.effort_id = segment_dict.get('id', None)

        try:
            self.activity_id = segment_dict.get('activity').get('id')
        except AttributeError:
            self.activity_id = None

        try:
            self.athlete_id = segment_dict.get('athlete').get('id')
        except AttributeError:
            self.athlete_id = None

        segment_details = segment_dict.get('segment')

        if segment_details is not None:
            for item in segment_var_list:
                setattr(self, item, segment_details.get(item))

            self.segment_id = segment_details.get('id')
            self.segment_resource_state = segment_details.get('resource_state')
            self.segment_name = segment_details.get('name')
            self.segment_distance = segment_details.get('distance')
        else:
            for item in segment_var_list:
                setattr(self, item, None)
            for item in segment_edit_list:
                setattr(self, item, None)


class Activity(Base):

    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True)
    athlete_id = Column(Integer, ForeignKey('athletes.strava_id'))  # EDITED
    resource_state = Column(Integer)
    name = Column(String)
    distance = Column(Float)
    moving_time = Column(Interval)
    elapsed_time = Column(Interval)
    total_elevation_gain = Column(Float)
    type = Column(String)
    workout_type = Column(Integer)
    strava_id = Column(Integer)
    external_id = Column(Integer)
    upload_id = Column(Integer)
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    timezone = Column(String)
    utc_offset = Column(Float)
    start_latlng = Column(MutableList.as_mutable(JList))
    end_latlng = Column(MutableList.as_mutable(JList))
    location_city = Column(String)
    location_state = Column(String)
    location_country = Column(String)
    start_latitude = Column(Float)
    start_longitude = Column(Float)
    achievement_count = Column(Integer)
    kudos_count = Column(Integer)
    comment_count = Column(Integer)
    athlete_count = Column(Integer)
    photo_count = Column(Integer)
    map = Column(MutableDict.as_mutable(JDict))
    trainer = Column(Boolean)
    commute = Column(Boolean)
    manual = Column(Boolean)
    private = Column(Boolean)
    visibility = Column(String)
    flagged = Column(Boolean)
    gear_id = Column(String)
    from_accepted_tag = Column(Boolean)
    average_speed = Column(Float)
    max_speed = Column(Float)
    average_temp = Column(Float)
    average_watts = Column(Float)
    kilojoules = Column(Float)
    device_watts = Column(Boolean)
    has_heartrate = Column(Boolean)
    heartrate_opt_out = Column(Boolean)
    display_hide_heartrate_option = Column(Boolean)
    elev_high = Column(Float)
    elev_low = Column(Float)
    pr_count = Column(Integer)
    total_photo_count = Column(Integer)
    has_kudoed = Column(Boolean)

    segment_con = relationship('Segment')

    def __init__(self, activity_dict):
        for item in activity_var_list:
            setattr(self, item, activity_dict.get(item, None))  # set all attrs from list

        for item in activity_date_fields:
            val = datetime.strptime(activity_dict.get(item, None), '%Y-%m-%dT%H:%M:%SZ')
            setattr(self, item, val)

        for item in activity_timedelta_fields:
            val = dt.timedelta(seconds=activity_dict.get(item, None))
            setattr(self, item, val)

        setattr(self, 'strava_id', activity_dict.get('id', None))
        # assign "id" field to 'strava_id' to preserve SQL id
        try:
            self.athlete_id = activity_dict.get('athlete').get('id')
        except AttributeError:
            self.athlete_id = None


class TempDir():
    """
    Context manager for working in a directory temporarily.
    """
    def __init__(self, path):
        self.old_dir = os.getcwd()
        self.new_dir = path

    def __enter__(self):
        os.chdir(self.new_dir)

    def __exit__(self, *args):
        os.chdir(self.old_dir)


def connect_to_db(engine_str, directory):
    """
    Example:
    engine, session, Base = connect_to_db('sqlite:///strava.sqlite', dir)

    Takes string name of the database to create/connect to, and the directory it should be in.

    engine_str: str, name of the database to create/connect to.

    directory: str/path, directory that the database should be made/connected to in.
        Requires context manager TempDir in order to work with async
    """

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    with TempDir(directory):
        engine = create_engine(engine_str)
    Session = sessionmaker(bind=engine)
    sess = Session()

    return engine, sess, Base