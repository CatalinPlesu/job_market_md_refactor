SERVICE=job_scraper.service
TIMER=job_scraper.timer
UNIT_DIR=/etc/systemd/system

install:
	sudo cp $(SERVICE) $(UNIT_DIR)/
	sudo cp $(TIMER) $(UNIT_DIR)/
	sudo systemctl daemon-reload
	sudo systemctl enable --now $(TIMER)

uninstall:
	sudo systemctl disable --now $(TIMER)
	sudo rm -f $(UNIT_DIR)/$(SERVICE) $(UNIT_DIR)/$(TIMER)
	sudo systemctl daemon-reload
