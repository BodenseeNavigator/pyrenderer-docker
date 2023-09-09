# pyrenderer-docker

1. build and run the `Dockerfile`
2. mount the /mount directory inside the container to /data
3. follow the following commands
```bash
# fetch osm file with all seamarks from openstreetmap database
wget -O /data/seamarks_bodensee.osm \
  --timeout=600 \
  --post-file=/data/overpass-api-bodensee.overpassql "http://overpass-api.de/api/interpreter"

# generate osm file extract
mkdir log
python3 /pyrenderer/pyextract.py -g -i /data/seamarks_bodensee.osm -o /data/extracts/ -x_min 268 -y_min 178 -x_max 269 -y_max 179

# generate tiles
python3 /pyrenderer/pyrenderer.py -i /data/extracts/osm_extracts/ -o /data/tiles/

```

## Additional resources
- pyrenderer github repository https://github.com/stevo01/pyrenderer/tree/master
- find map bounds https://www.openstreetmap.org/export#map=10/47.7199/9.3240
