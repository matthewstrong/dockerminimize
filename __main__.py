import argparse
import logging

from .depsolver import *
from .gst import *

def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    file_list = set()
    if args.gst_base or args.add_gst_plugin:
        files = collect_plugins(args.add_gst_plugin)
        file_list = file_list.union(files)

    if args.add_file:
        files = collect_files(args.add_file)
        file_list = file_list.union(files)

    file_list = sorted(file_list)
    if args.copy_to:
        copy_files(file_list, args.copy_to)
    if args.stdout:
        print('\n'.join(str(f) for f in file_list))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-file',
                        metavar=('FILE'),
                        nargs='+',
                        default=[],
                        help='Add ELF binary or library')
    group1 = parser.add_argument_group('Output Options')
    group1.add_argument('--stdout',
                        action='store_true',
                        help='Print the file list to stdout')
    group1.add_argument('--copy-to',
                        metavar=('DEST'),
                        help='Copy the file list to the destination path')

    group2 = parser.add_argument_group('GStreamer Options')
    group2.add_argument('--gst-base',
                        action='store_true',
                        help='Include the base set of GStreamer plugins')
    group2.add_argument('--add-gst-plugin',
                        metavar=('NAME'),
                        nargs='+',
                        default=[],
                        help='Include dependencies for plugin')

    group3 = parser.add_argument_group('Logging options')
    group3.add_argument('--verbose',
                       action='store_const',
                       const=logging.INFO,
                       dest='loglevel')
    group3.add_argument('--debug',
                       action='store_const',
                       const=logging.DEBUG,
                       dest='loglevel')
    parser.set_defaults(loglevel=logging.WARN)

    return parser.parse_args()

def collect_plugins(plugins):
    min = GstMinimize()
    for name in plugins:
        min.add_plugin(name)
    return min.get_files()

def collect_files(files):
    solver = DependencySolver()
    solver.add(files)
    ret = set(files).union(solver.get_files())
    return ret

def copy_files(file_list, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)

    for file in file_list:
        cmd = "cp --parents --target-directory={} {}".format(dest, file)
        LOG.info("Running command: %s", cmd)
        subprocess.check_call(shlex.split(cmd))

if __name__ == '__main__':
    main()
