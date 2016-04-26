# Releasing an app means loading the app.tar.gz file on an appscale instance
app.tar.gz:
	tar --exclude='app.tar.gz' -czvf app.tar.gz *

release: clean app.tar.gz
	#Deploy to appserver?

# local dev server
dev:
	dev_appserver.py .
setup: clean
	pip install -t lib google-api-python-client
	pip install -t lib identity-toolkit-python-client

clean:
	rm -rf lib/*
	if [ -a app.tar.gz ]; then rm app.tar.gz; fi;