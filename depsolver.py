import sys, os, argparse, logging
import subprocess, shlex
import re
import collections, types

LOG = logging.getLogger(__name__)

class DependencySolver(object):
    def __init__(self):
        self.deps = set()

    def add(self, path):
        """Accept both string and string collections as arguments"""
        if isinstance(path, collections.Iterable) and not isinstance(path, types.StringTypes):
            for p in path: self.add(p)
            return

        ## Validate the file path
        # TODO
        ## Validate input is ELF file
        # TODO
        ## Resolve the dependencies
        out = subprocess.check_output(['ldd', path])
        for line in out.splitlines():
            ## Match dynamic file dependency
            match_shlib = re.match(r'\t.* => (.*) \(0x', line)
            ## Match static file dependency (likely ld-linux.so)
            match_ldso = re.match(r'\t(/.*) \(0x', line)

            match = match_shlib if match_shlib else match_ldso
            if match:
                LOG.debug('file: %s, needs: %s', os.path.basename(path), match.group(1))
                self.deps.add(match.group(1))

    def get_files(self):
        return self.deps

def copy_file(src, dest):
    if not os.path.isdir(dest):
        os.makedirs(dest)

    cmd = "cp --parents --target-directory={} {}".format(dest, src)
    LOG.info("Running command: %s", cmd)
    subprocess.check_call(shlex.split(cmd))

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add-file', '-a',
                        metavar=('FILE'),
                        nargs='+',
                        default=[],
                        help='Add ELF binary or library')
    parser.add_argument('--copy-to',
                        metavar=('DEST'),
                        help='Destination path to copy all of the dependencies.')
    group = parser.add_argument_group('Logging options')
    group.add_argument('--verbose',
                       action='store_const',
                       const=logging.INFO,
                       dest='loglevel')
    group.add_argument('--debug',
                       action='store_const',
                       const=logging.DEBUG,
                       dest='loglevel')
    parser.set_defaults(loglevel=logging.WARN)

    return parser.parse_args()

def main():
    args = parse_args()
    logging.basicConfig(level=args.loglevel)

    solv = DependencySolver()
    for file in args.add_file:
        solv.add(file)

    all_files = set(args.add_file).union(solv.get_files())
    for file in sorted(all_files):
        print file

    if args.copy_to:
        print "Copying files to: %s" % args.copy_to
        for file in sorted(all_files):
            copy_file(file, args.copy_to)

    # print solv.get_deps()
    # min = GstMinimize()
    # for name in args.add_plugin:
    #     min.add_plugin(name)
    # for file in min.get_files():
    #     print file

if __name__ == '__main__':
    main()
