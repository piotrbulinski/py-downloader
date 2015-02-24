# py-downloader
Python Concurrent Downloader

    usage: downloader.py [-h] [-c CONCURRENCY] [-s PART_SIZE]
                         [-p PARTS [PARTS ...]] [-o OUTPUT] [-q]
                         url

    positional arguments:
      url

    optional arguments:
      -h, --help            show this help message and exit
      -c CONCURRENCY, --concurrency CONCURRENCY
                            number of concurrent download threads
      -s PART_SIZE, --part-size PART_SIZE
                            part size
      -p PARTS [PARTS ...], --parts PARTS [PARTS ...]
                            parts
      -o OUTPUT, --output OUTPUT
                            output file
      -q                    quite mode
