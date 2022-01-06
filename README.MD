# gyroscope2gpx

This little python joint will do you a favor of taking your "Travel" export 
from Gyroscope (https://gyrosco.pe) and turn it into a bunch of daily GPX
files. Maybe you need this for some reason!

## Usage!

1. Clone this repository and install dependencies
   1. Must use Python3
   2. `pip install -r requirements.txt`
2. Go to https://gyrosco.pe/export/
3. Export your "Travels" csv file
4. Run the script (help below)
   1. example: `./gyroscope2gpx myexport.csv`

```
usage: gyroscope2gpx.py [-h] [-o OUTPUTDIR] [--debug] inputfile

Reads a 'Travels' CSV export from Gyroscope and converts to daily GPX files.

positional arguments:
  inputfile             csv file from Gyroscope

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        (optional) directory to output GPX files, defaults to ./gyroscope2gpx_output
  --debug
```

## Important stuff to be aware of

There are a few caveats with how this data exports from Gyroscope and is thusly
processed:

1. Gyroscope does not include time data for each point in a segment, only start
   and end times for the segment
2. Because of #1, this little script assumes that the points are equidistantly 
   spaced in time across that interval.
3. This means that the track will indicate you traveled at constant velocity 
   throughout that time interval (impressive, if not astronomically impossible)
4. There is no elevation data, so we use a third party library to load it,
   which requires an internet connection and a few gigabytes of data to
   download, depending on where you've been in the world (only once!)

Because of these caveats, these tracks are probably not well used for say, 
uploading to Strava, or something. However, they might be reasonably useful 
for geotagging your 35mm photos (my use case!)

If you'd like to see something change in the data provided by Gyroscope, try
[support@gyrosco.pe](mailto:support@gyrosco.pe) :)

### Subsequent executions, updating data

If a GPX file already exists in the output directory, it will be skipped. If 
you need to overwrite a file for any reason, delete it yourself and run the 
script.

### Elevation data

Elevation data is provided by the [SRTM.py][1] library, which has this to say:

> On every elevation requested the library will:
> 1. Check if the SRTM file is stored locally
> 2. If not -- download it from NASA servers and store locally 
>    (in ./.srtmcache/)
> 3. Parse elevations from it

This could mean quite a bit of data needs to be downloaded, so beware
(my export needed about 2.29gb of elevation data!)

I could make this part optional, I guess? Create an issue!

[1]: <https://github.com/tkrajina/srtm.py> "SRTM.py"

### Follow me on Gyrosco.pe:

https://gyrosco.pe/ngordon779/

## License

This software is licensed under the GNU GPLv3. See file COPYING.