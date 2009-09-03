SUBDIRS = Parser OutputDevs

guiltydir = $(pyexecdir)/Guilty

guilty_PYTHON = 	\
	__init__.py	\
	Blame.py	\
	Config.py	\
	main.py		\
	utils.py

CLEANFILES = _config.py
EXTRA_DIST = _config.py.in

all-local: _config.py

_config.py: _config.py.in
	sed							\
		-e s!\@PACKAGE_NAME\@!$(PACKAGE_NAME)!		\
		-e s!\@PACKAGE_VERSION\@!$(PACKAGE_VERSION)!	\
		< $< > $@
