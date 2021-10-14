PREFIX ?= /usr/local


install: $(PREFIX)/bin/debian-feed \
	$(PREFIX)/lib/systemd/system/debian-feed.service \
	$(PREFIX)/lib/systemd/system/debian-feed.timer \
	systemctl enable debian-feed.timer
	systemctl start debian-feed.timer

uninstall:
	systemctl stop debian-feed.timer
	systemctl disable debian-feed.timer
	systemctl stop debian-feed-boot.service
	rm $(PREFIX)/bin/debian-feed \
		$(PREFIX)/etc/debian-feed.json \
		$(PREFIX)/lib/systemd/system/debian-feed.service \
		$(PREFIX)/lib/systemd/system/debian-feed.timer

$(PREFIX)/bin/debian-feed: $(PREFIX)/etc/debian-feed.json
	cp debian-feed.py $(PREFIX)/bin/debian-feed

$(PREFIX)/etc/debian-feed.json:
	cp debian-feed.json $@

$(PREFIX)/lib/systemd/system/debian-feed.timer: $(PREFIX)/lib/systemd/system
	cp debian-feed.timer $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system/debian-feed-boot.service: $(PREFIX)/lib/systemd/system
	cp debian-feed-boot.service $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system/debian-feed.service: $(PREFIX)/lib/systemd/system
	cp debian-feed.service $(PREFIX)/lib/systemd/system/

$(PREFIX)/lib/systemd/system:
	mkdir -p $(PREFIX)/lib/systemd/system
