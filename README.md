# handout-downloader
A _Python_ script for downloading **entire directories** from the FH-Wedel [handout server](https://stud.fh-wedel.de/handout/).

```bash
$ ./handout-download.py /Iwanowski/Berechenbarkeit/ berchenbarkeit/
Username: its101337
Password:
14:56:36: Listing files recursivly...
14:56:36: Downloading 52 files to target directory "berechenbarkeit/"
100%|███████████████████████████████████████████████████████████| 52/52 [00:01<00:00, 24.32it/s]
14:56:38: Finished downloading!
```

**Requires valid FH-Wedel credentials for authentication.**

## Install

A `requirements.txt` is provided to install all required packages using `pip`.

```bash
pip install -r requirements.txt
```


## 2. Download

```bash
./handout-download.py HANDOUT-SOURCE LOCAL-TARGET [--max-size MAX_SIZE]
```
The optional `MAX_SIZE` parameter specifies file size limit in MB and defaults to 128MB.

You will be asked to enter your username and password for your FH-Wedel account.
## 3. ???

## 4. Profit!