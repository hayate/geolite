# -*- coding: utf-8 -*-
import os
import re
import sys
import tarfile
import httplib
import logging
import tempfile

import requests

GEOLITE_CITY_URL = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def download(url):
    """download compressed file"""
    resp = requests.get(url, stream=True)
    if resp.status_code != httplib.OK:
        msg = "Failed to download: {0} status code: {1}"
        logger.error(msg.format(url, resp.status_code))
        return
    try:
        # retrieve file name from header
        m = re.search("filename=(.+)",
                      resp.headers.get('Content-Disposition'))
        filename = m.group(1)
        filepath = "{0}/{1}".format(tempfile.gettempdir(), filename)
        # save file in "tmp" directory
        with open(filepath, 'wb') as fp:
            fp.write(resp.content)
            return fp.name
    except Exception:
        logger.exception("Failed to download: {0}".format(url))


def extract(filepath):
    """uncompress and extract file"""
    tmpdir = tempfile.gettempdir()
    with tarfile.open(name=filepath, mode='r:gz') as tf:
        for ti in tf.getmembers():
            if ti.name.endswith('.mmdb'):
                tf.extract(ti, tmpdir)
                return "{0}/{1}".format(tmpdir, ti.name)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.error("Missing filepath in command line")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]):
        logger.error("Path: {0} does not exist".format(sys.argv[1]))
        sys.exit(1)
    filepath = download(GEOLITE_CITY_URL)
    filepath = extract(filepath)
    # mv file to given directory
    os.rename(filepath, "{0}/{1}".format(sys.argv[1].rstrip("\//"),
                                         os.path.basename(filepath)))
