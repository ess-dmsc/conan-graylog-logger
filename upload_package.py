#!/usr/bin/env python

import argparse
import os
import conanfile


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('remote')
    arg_parser.add_argument('version')
    arg_parser.add_argument('user')
    arg_parser.add_argument('channel')

    args = arg_parser.parse_args()

    cmd = """conan upload --all --remote {} {}/{}@{}/{}""".format(
        args.remote,
        conanfile.GraylogloggerConan.name,
        args.version,
        args.user,
        args.channel
    )

    os.system(cmd)
