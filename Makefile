PREFIX ?= /usr/local


install: $(PREFIX)/bin/ubuntu-feed \
	$(PREFIX)/lib/systemd/system/ubuntu-feed.service \
	$(PREFIX)/lib/systemd/system/ubuntu-feed.timer
	systemctl enable ubuntu-feed.timer
	systemctl start ubuntu-feed.timer

install-debian-deps:
	apt install python3-bs4 \
		python3-feedgen \
		python3-feedparser \
		python3-lxml \
		python3-requests

uninstall:
	systemctl stop ubuntu-feed.timer
	systemctl disable ubuntu-feed.timer
	rm $(PREFIX)/bin/ubuntu-feed \
		$(PREFIX)/etc/ubuntu-feed.json \
		$(PREFIX)/lib/systemd/system/ubuntu-feed.service \
		$(PREFIX)/lib/systemd/system/ubuntu-feed.timer

$(PREFIX)/bin/ubuntu-feed: $(PREFIX)/etc/ubuntu-feed.json
	cp ubuntu-feed.py $(PREFIX)/bin/ubuntu-feed

$(PREFIX)/etc/ubuntu-feed.json:
	cp ubuntu-feed.json $@

$(PREFIX)/lib/systemd/system/ubuntu-feed.timer: $(PREFIX)/lib/systemd/system
	cp ubuntu-feed.timer $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system/ubuntu-feed-boot.service: $(PREFIX)/lib/systemd/system
	cp ubuntu-feed-boot.service $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system/ubuntu-feed.service: $(PREFIX)/lib/systemd/system
	cp ubuntu-feed.service $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system:
	mkdir -p $(PREFIX)/lib/systemd/system
