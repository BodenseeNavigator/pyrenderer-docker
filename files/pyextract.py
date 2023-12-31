'''
Created on Dec 31, 2020

@author: stevo
'''
import os
import json
import argparse
import timeit
from utils.map_bb import num2MapBB, conversion_type
from utils.file_and_folder import ensure_dir
from utils.glog import logger_init
from logging import INFO, DEBUG
from utils.proc import ExecuteCmdExt


def write_configfile(filename, outdir, maplist):

    data = {}
    data['extracts'] = []
    data['directory'] = outdir

    for x, y, z, smap in maplist:
        data['extracts'].append({'output': '{}-{}-{}.osm'.format(x, y, z),
                                 'output_format': 'osm',
                                 'bbox': smap.getbbox()})

    with open(filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == '__main__':

    start = timeit.default_timer()

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('-i',
                        dest='inputfilename',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        default="./sampledata/in/seamarks_planet.osm",
                        help='name of osm file')

    parser.add_argument('-o',
                        dest='outdir',
                        default="./workingdir/",
                        help='output directory')

    parser.add_argument('-y_min',
                        dest='y_min_z9',
                        type=int,
                        default=161,
                        help='x position of tile (zoomlevel 9)')

    parser.add_argument('-y_max',
                        dest='y_max_z9',
                        type=int,
                        default=161,
                        help='x position of tile (zoomlevel 9)')

    parser.add_argument('-x_min',
                        dest='x_min_z9',
                        type=int,
                        default=274,
                        help='x position of tile (zoomlevel 9)')

    parser.add_argument('-x_max',
                        dest='x_max_z9',
                        type=int,
                        default=274,
                        help='x position of tile (zoomlevel 9)')

    parser.add_argument('-x',
                        dest='x',
                        type=int,
                        default=-1,
                        help='x position of tile (zoomlevel 9)')

    parser.add_argument('-y',
                        dest='y',
                        type=int,
                        default=-1,
                        help='y position of tile (zoomlevel 9)')

    parser.add_argument('-g', '--generate', action='store_true')

    parser.add_argument('-l',
                        dest='logfilename',
                        default="./log/pyextract.log",
                        help='logfile')

    args = parser.parse_args()

    log = logger_init("pyextractr",
                      args.logfilename,
                      level_file=DEBUG,
                      level_console=INFO)

    in_filename = args.inputfilename.name
    z = 9  # zoomlevel

    if args.x is not -1 and args.y is not -1:
        x_min_z9 = args.x
        x_max_z9 = args.x
        y_min_z9 = args.y
        y_max_z9 = args.y
    else:
        x_min_z9 = args.x_min_z9
        x_max_z9 = args.x_max_z9
        y_min_z9 = args.y_min_z9
        y_max_z9 = args.y_max_z9

    print("generate config file for command \"osmium extract\": {}".format(in_filename))
    print("input file: {}".format(in_filename))
    print("output dir: {}".format(args.outdir))
    print("x_min={}, x_max={}, y_min={}, y_max={}, z={}".format(x_min_z9, x_max_z9, y_min_z9, y_max_z9,z))

    # stage 1 / generate config file with level 9
    maplist = list()

    for y_z9 in range(y_min_z9, y_max_z9+1):
        for x_z9 in range(x_min_z9, x_max_z9+1):
            maplist.append([x_z9, y_z9, z, num2MapBB(x_z9, y_z9, z, conversion_type.extendet)])

    confdir = args.outdir + "cfg/"
    ensure_dir(confdir)
    outfile = confdir + "osmium_extract_z9.cfg"

    if os.path.exists(outfile):
        os.remove(outfile)

    osmdir = args.outdir + "osm-extracts/"
    ensure_dir(osmdir)

    log.info('write_configfile: {}'.format(outfile))
    write_configfile(outfile, osmdir, maplist)
    convert_cmd = "osmium extract --overwrite --config {} {}".format(outfile, in_filename)
    log.info(convert_cmd)

    if(args.generate is True):
        outstr, ret = ExecuteCmdExt(convert_cmd)
        if ret != 0:
            log.info("generation failed outfile: {}".format("outfile"))
            log.error(outstr)
        else:
            log.info("generation passed outfile: {}".format("outfile"))

    # stage 2 / generate config file with level 10-12
    for y_z9 in range(y_min_z9, y_max_z9+1):
        for x_z9 in range(x_min_z9, x_max_z9+1):

            in_filename = osmdir + "{}-{}-{}.osm".format(x_z9, y_z9, z)

            filesize = os.stat(in_filename).st_size
            if filesize < 100:
                log.info("generation skipped for in_filename {}".format(in_filename))
                continue

            maplist = list()
            for xadj_z10 in [0, 1]:
                for yadj_z10 in [0, 1]:
                    x_z10 = x_z9 * 2 + xadj_z10
                    y_z10 = y_z9 * 2 + yadj_z10
                    maplist.append([x_z10, y_z10, 10, num2MapBB(x_z10, y_z10, 10, conversion_type.extendet)])

            for xadj_z11 in [0, 1, 2, 3]:
                for yadj_z11 in [0, 1, 2, 3]:
                    x_z11 = x_z9 * 4 + xadj_z11
                    y_z11 = y_z9 * 4 + yadj_z11
                    maplist.append([x_z11, y_z11, 11, num2MapBB(x_z11, y_z11, 11, conversion_type.extendet)])

            for xadj_z12 in [0, 1, 2, 3, 4, 5, 6, 7]:
                for yadj_z12 in [0, 1, 2, 3, 4, 5, 6, 7]:
                    x_z12 = x_z9 * 8 + xadj_z12
                    y_z12 = y_z9 * 8 + yadj_z12
                    maplist.append([x_z12, y_z12, 12, num2MapBB(x_z12, y_z12, 12, conversion_type.extendet)])

            outfile = confdir + "osmium_extract_x{}-y{}_z9.cfg".format(x_z9, y_z9)

            if os.path.exists(outfile):
                os.remove(outfile)

            write_configfile(outfile, osmdir, maplist)
            log.info('write_configfile {}'.format(outfile))
            convert_cmd = "osmium extract --overwrite --config {} {}".format(outfile, in_filename)
            log.info(convert_cmd)

            if(args.generate is True):
                outstr, ret = ExecuteCmdExt(convert_cmd)
                if ret != 0:
                    log.info("generation failed / outfile: {}".format(outfile))
                    log.error(outstr)
                else:
                    log.info("generation passed / outfile: {}".format(outfile))

    stop = timeit.default_timer()
    print('Time: ', stop - start)
