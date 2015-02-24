#!/usr/bin/env python3.4
import os
import logging
import argparse
import math
import threading

from urllib import request, error


BUFFER_SIZE = 64 * 1024


log = logging.getLogger(__name__)


def receive(in_fd, out_fd, nbytes):
    in_fd_read = in_fd.read
    out_fd_write = out_fd.write
    while nbytes > 0:
        nbytes -= out_fd_write(in_fd_read(BUFFER_SIZE))

    return 0


def get_part(url, output, bytes_from, bytes_to):
    log.debug('getting bytes %s - %s', bytes_from, bytes_to)

    req = request.Request(
        url,
        headers=dict(range='bytes=%s-%s' % (bytes_from, bytes_to)))

    try:
        resp = request.urlopen(req)
    except (error.HTTPError, error.URLError) as exc:
        log.error(str(exc))
        return 1

    with open(output, 'r+b') as fp:
        fp.seek(bytes_from)
        ret = receive(resp, fp, bytes_to - bytes_from + 1)

    log.debug('bytes %s - %s completed', bytes_from, bytes_to)
    return ret


def get(url, output, concurrency=1, part_size=None, parts=None):
    log.debug('Getting %s -> %s', url, output)
    log.debug('Concurrency: %s', concurrency)

    try:
        resp = request.urlopen(url)
    except (error.HTTPError, error.URLError) as exc:
        return log.error(str(exc))

    if resp.getheader('accept-ranges', '') != 'bytes':
        concurrency = 1
        log.warning('range requests not supported')

    filesize = None
    try:
        filesize = int(resp.getheader('content-length', ''))
    except (TypeError, ValueError):
        concurrency = 1
        log.warning('cannot get the filesize')
    else:
        log.debug('File size: %s', filesize)

    if part_size is None or parts is None:
        log.debug('preallocating space for the file')
        with open(output, 'wb') as fp:
            #fp.seek(filesize-1)
            fp.write(b'\0')

        resp.close()

        log.debug('starting multi part download')
        part_size = math.ceil(filesize / concurrency)
        parts = list(range(concurrency))
    log.debug('part size: %s', part_size)
    log.debug('downloading parts: %s', ', '.join(map(str, parts)))

    threads = []
    for part in parts:
        t = threading.Thread(
            target=get_part,
            kwargs=dict(
                url=url,
                output=output,
                bytes_from=part * part_size,
                bytes_to=min((part+1) * part_size, filesize) - 1))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--concurrency', type=int, default=1,
                        help="number of concurrent download threads")

    parser.add_argument('-s', '--part-size', type=int, default=1,
                        help="part size")

    parser.add_argument('-p', '--parts', type=int, nargs='+',
                        help="parts")

    parser.add_argument('-o', '--output', type=str,
                        help="output file")

    parser.add_argument('-q', action='store_true', default=False,
                        help='quite mode')

    parser.add_argument('url', type=str)
    args = parser.parse_args()

    if args.q:
        log.setLevel(logging.ERROR)
    else:
        log.setLevel(logging.DEBUG)

    log_format = '[%(asctime)-15s] %(message)s'
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter(log_format))
    log.addHandler(log_handler)

    output_file = args.output or \
        args.url.split('/')[-1].split('?')[0] or \
        'index.html'

    if os.path.exists(output_file) and not args.parts:
        exit("File already exist!")

    get(url=args.url, output=output_file, concurrency=args.concurrency,
        part_size=args.part_size, parts=args.parts)
