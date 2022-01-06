#!/usr/bin/env python3
import argparse
from datetime import timedelta
import os
import csv
import dateparser
from itertools import groupby
import logging
import gpxpy.gpx
import srtm

logging.basicConfig()
_LOGGER_ = logging.getLogger(__name__)

_description_ = "Reads a 'Travels' CSV export from Gyroscope and converts to daily GPX files."

def parse_args():
  def dir_path(string):
      if os.path.isdir(string):
        return string
      else:
        os.mkdir(string)
  parser = argparse.ArgumentParser(description=_description_)
  parser.add_argument('inputfile', 
      type=argparse.FileType('r', encoding='UTF-8'), 
      help='csv file from Gyroscope')
  parser.add_argument('-o','--outputdir',
      type=dir_path,
      default="./gyroscope2gpx_output/",
      help="directory to output GPX files (automatically created)")
  parser.add_argument('--debug', action="store_true")
  return parser.parse_args()

def load_gyroscope_data(csvstream):
  _LOGGER_.info('Loading input csv...')
  gyroscope_data = []
  reader = csv.DictReader(csvstream)
  for row in reader:
    points = row['Points'].split('),(')
    for i, point in enumerate(points):
      points[i] = tuple(point.replace('(','').replace('),','').split(', '))
    gyroscope_data.append({
      'start_time': dateparser.parse(row['Start Time']),
      'end_time': dateparser.parse(row['End Time']),
      'type': row['Type'],
      'points': points,
      'source_service': row['Service']
    })
  _LOGGER_.info('Done.')
  return gyroscope_data

def group_gyroscope_data(data):
  _LOGGER_.info('Grouping Gyroscope data into segments...')
  gyroscope_data = {}
  group_func = lambda x: x['start_time'].date()
  for day, segments in groupby(data, group_func):
    gyroscope_data[day] = sorted(list(segments), key=lambda x: x['start_time'])
  _LOGGER_.info('Done.')
  return gyroscope_data

def create_gpx_from_gyroscope_segments(segments):
  _LOGGER_.debug("Creating GPX from {} segments...".format(len(segments)))
  gpxout = gpxpy.gpx.GPX()
  gpxout.creator = "gyroscope2gpx - by snicker"
  
  gpx_track = gpxpy.gpx.GPXTrack()
  gpxout.tracks.append(gpx_track)

  for segi, segment in enumerate(segments):
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    segment_start = segment['start_time']
    segment_end = segment['end_time']
    segment_total_time = float((segment_end - segment_start).total_seconds())
    segment_points = segment['points']
    segment_time_between_points = \
      segment_total_time / max(1,(len(segment_points) - 1))

    _LOGGER_.debug("segment {} {}".format(segi,segment['type']))
    _LOGGER_.debug("from {} to {}".format(segment_start,segment_end))
    _LOGGER_.debug("segment {} total time {}s".format(segi,segment_total_time))
    _LOGGER_.debug("segment {} points {}".format(segi,len(segment_points)))
    _LOGGER_.debug("segment {} time between {}s".format(segi,segment_time_between_points))

    for pti, pt in enumerate(segment_points):
      delta = timedelta(seconds=segment_time_between_points * pti)
      pttime = segment_start + delta
      gpxpt = gpxpy.gpx.GPXTrackPoint(float(pt[0]),float(pt[1]),time=pttime)
      gpx_segment.points.append(gpxpt)

  _LOGGER_.debug('Adding elevation data...')
  elevation_data = srtm.get_data(local_cache_dir=".")
  elevation_data.add_elevations(gpxout)

  _LOGGER_.debug("Done creating GPX.")
  return gpxout

def main():
  args = parse_args()

  _LOGGER_.setLevel(logging.INFO)
  if args.debug:
    _LOGGER_.setLevel(logging.DEBUG)

  data = load_gyroscope_data(args.inputfile)
  grouped_data = group_gyroscope_data(data)
  for day in grouped_data:
    day_format = day.strftime("%Y%m%d")
    basename = "{}_gyroscope.gpx".format(day_format)
    filename = os.path.join(args.outputdir,basename)
    gpx = create_gpx_from_gyroscope_segments(grouped_data[day])
    gpx.name = "Gyroscope path: {}".format(day_format)

    _LOGGER_.info("Writing {}...".format(filename))
    with open(filename,'w') as gpxfile:
      gpxfile.write(gpx.to_xml())
    

if __name__ == "__main__":
  main()