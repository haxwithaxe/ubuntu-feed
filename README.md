# Description
This generates an RSS file that can be used by torrent clients to automatically download Ubuntu installers and live media. It can be used with any repository that has the same layout as [releases.ubuntu.com](https://releases.ubuntu.com).

# Installation
The following packages need to be installed. You can use your OS's package manager or `pip install -r requirements.txt`.
* beautifulsoup4
* feedgenerator
* feedparser
* lxml
* requests

1. `git clone https://github.com/haxwithaxe/ubuntu-feed.git`
1. `cd debian-feed`
1. If you're using a Debian based distro you can install the dependencies with `make install-debian-deps`
1. `make install` or `PREFIX=/whatever/install/path/you/want make install`
1. Edit the feed path in `/usr/local/etc/debian-feed.json`.
1. `systemctl start ubuntu-feed.timer`

# Configuration
Example ubuntu-feed.json:
```
{
	"file_extension": ".torrent", 
	"rss_file": "/path/to/ubuntu-feed.rss", 
	"sources": [
		"https://releases.ubuntu.com"
	]
}
```
* `file_extention` should always be `.torrent` but can be changed to `.iso` or `.jigdo` with the appropriate `sources` to get a feed with iso/jigdo file links instead of torrent links.
* `rss_file` is the path to where the torrent client can get to the feed. If you put it in a web server's file directory you can get to it via the web but your torrent client might be fine with a file URI (eg `file:///path/to/ubuntu-feed.rss`).
* `sources` is a list of URLs to look for torrents in. These must point to the releases pages. ubuntu-feed does not spider around looking for the releases page.
