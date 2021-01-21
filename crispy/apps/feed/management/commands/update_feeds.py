#!python3
import threading
from queue import Queue
import time

# lock to serialize console output
import feedparser
from django.conf import settings
from django.core.management import BaseCommand

from crispy.apps.feed.models import Feed
from crispy.apps.feed.scraper import Scraper

lock = threading.Lock()

# Create the queue
q = Queue()


def do_work(feed):
    print('Starting work on {}'.format(feed))
    time.sleep(.1)  # pretend to do some lengthy work.
    # Make sure the whole print completes or threads can mix up output in one line.
    with lock:
        print(threading.current_thread().name, feed)
        scraper = Scraper(feedparser.parse, feed)
        updated, parsed_feed = scraper.check_feed()

        if updated:
            print('Found updates for feed {}'.format(feed))
            feed.update_feed_data(parsed_feed)
            feed.update_feed_entries(parsed_feed.entries)
            feed.save()
        else:
            print('No updates for feed {}'.format(feed))

        print('Feed {} done'.format(feed))


# The worker thread pulls an item from the queue and processes it
def worker():
    while True:
        feed = q.get()
        do_work(feed)
        q.task_done()


# Create thread pool
for i in range(settings.NUM_WORKERS):
    t = threading.Thread(target=worker)
    t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
    t.start()

# stuff work items on the queue
feeds = Feed.objects.active().all()
start = time.perf_counter()

for f in feeds:
    q.put(f)

# block until all tasks are done
q.join()


class Command(BaseCommand):
    help = 'Updates feeds every N seconds. Everlasting command.'

    def add_arguments(self, parser):
        parser.add_argument('seconds', nargs='?', type=int, default=10)

    def handle(self, *args, **options):
        print('time:', time.perf_counter() - start)
