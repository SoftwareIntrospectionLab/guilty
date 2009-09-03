SUBDIRS = Parser OutputDevs

guiltydir = $(pyexecdir)/Guilty

guilty_PYTHON = 	\
	__init__.py	\
	Blame.py	\
	main.py		\
	utils.py

CLEANFILES = config.py
EXTRA_DIST = config.py.in

all-local: config.py

config.py: config.py.in
	sed							\
		-e s!\@PACKAGE_NAME\@!$(PACKAGE_NAME)!		\
		-e s!\@PACKAGE_VERSION\@!$(PACKAGE_VERSION)!	\
		< $< > $@
