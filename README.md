
# Table of Contents

1.  [Coursera-lecture-downloader](#orgd29b31f)
    1.  [Licence](#org0b1364d)
    2.  [Requirements](#org6402008)
    3.  [Usage](#orgfae5329)


<a id="orgd29b31f"></a>

# Coursera-lecture-downloader

A small script to download Coursera's lecture in local for off Internet consultation.


<a id="org0b1364d"></a>

## Licence

DWTFYW  (Do What &#x2026; You Want !)


<a id="org6402008"></a>

## Requirements

-   Python 3.5 and selenium


<a id="orgfae5329"></a>

## Usage

The script opens a navigator and connects to a coursera course.
It logs in.  If it asks for captcha, answer it manualy.  The program will pause and wait until you finish and confirm in the prompt.

It collects the urls for the lecture videos and downloads them where you want.

    python video_scrapping_p35.py -h 
    
    will give the following options
      -h, --help            show this help message and exit
      --mtp MTP, -p MTP     required: your coursera mtp
      --email EMAIL, -e EMAIL
    			required: your coursera login (or email)
      --courseName COURSENAME, -c COURSENAME
    			required: the courseName, for example: python-machine-learning
      --time TIME, -t TIME  to slow down the bot.  leave the default if you have a good connection
      --week WEEK WEEK, -w WEEK WEEK
    			default: 1 4, two numbers representing the first and last course week from wich to download the video lectures
      --destDir DESTDIR, -d DESTDIR
    			default: ~/Videos/Coursera/, the destination dir where video lecture will download
      --headless, -H        If present will run the scrapping in background.  Don't use it because coursera will often ask for catptcha.

