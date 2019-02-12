#!/usr/bin/env python3
import requests
import os
import argparse
import logging
from tqdm import tqdm
from threading import Thread
from queue import Queue
from getpass import getpass
from bs4 import BeautifulSoup
from urllib.parse import unquote

HANDOUT_URL = 'https://stud.fh-wedel.de/handout'


def is_relevant(link):
    irrelevant = set(['Name', 'Last modified', 'Size', 'Parent Directory'])
    return link.text != '' and not link['href'].startswith('#') and link.text not in irrelevant


def list_worker(list_queue, file_queue, creds):
    while True:
        list_url = list_queue.get()
        if list_url is not None:
            dir_req = requests.get(list_url, auth=creds)
            page = BeautifulSoup(dir_req.text, 'html.parser')
            table = page.find('table')
            links = sorted(set(link['href'] for link in filter(
                is_relevant, table.find_all('a')))) if table else []
            for link in links:
                if link.endswith('/'):
                    logging.debug('Following link %s', link)
                    list_queue.put(list_url + link)
                else:
                    file_queue.put(list_url + link)
            list_queue.task_done()


def download_worker(file_queue, source, target, max_size, creds, pbar):
    while True:
        file_url = file_queue.get()
        if file_url is not None:
            file_req = requests.get(file_url, auth=creds, stream=True)
            size_in_mb = int(file_req.headers['Content-length']) / 1_000_000
            path = '/' + unquote(file_url[len(HANDOUT_URL + source):])
            if size_in_mb > max_size:
                logging.debug(
                    'Skipping large file %s, Size: %.3fM', path, size_in_mb)
            else:
                logging.debug('Dowloading file %s, Size: %.3fM',
                              path, size_in_mb)
                os.makedirs(os.path.dirname(target + path), exist_ok=True)
                with open(target + path, 'wb') as f:
                    f.write(file_req.content)
            pbar.update(1)
            file_queue.task_done()


def list_files(source, list_queue, file_queue, creds):
    num_list_threads = 32
    logging.info('Listing files recursivly...')
    list_queue.put(HANDOUT_URL + source)

    for _ in range(num_list_threads):
        worker = Thread(target=list_worker, args=[
                        list_queue, file_queue, creds])
        worker.setDaemon(True)
        worker.start()

    list_queue.join()
    return file_queue.qsize()


def download_files(num_files, file_queue, source, target, max_size):
    num_download_threads = 64
    logging.info('Downloading %d files to target directory "%s"',
                 num_files, target)
    pbar = tqdm(total=num_files)

    for _ in range(num_download_threads):
        worker = Thread(target=download_worker, args=[
                        file_queue, source, target, max_size, creds, pbar])
        worker.setDaemon(True)
        worker.start()

    file_queue.join()
    pbar.close()
    logging.info('Finished downloading!')


def run(source, target, max_size, creds):
    list_queue = Queue()
    file_queue = Queue()
    num_files = list_files(source, list_queue, file_queue, creds)
    download_files(num_files, file_queue, source, target, max_size)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s: %(message)s',
                        datefmt='%H:%M:%S', level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='handout directory to download')
    parser.add_argument('target', help='local download path')
    parser.add_argument('-m', '--max-size', type=int,
                        default=128, help='file size limit in MB')
    args = parser.parse_args()
    creds = (input('Username: '), getpass())
    run(args.source, args.target, args.max_size, creds)
