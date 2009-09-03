AC_PREREQ(2.57)
AC_INIT([Guilty],[1.0])
AM_INIT_AUTOMAKE([1.9 dist-bzip2 no-dist-gzip])

AM_MAINTAINER_MODE

AM_PATH_PYTHON(2.4)

PKG_CHECK_MODULES(REPOSITORY_HANDLER, repositoryhandler)

AC_MSG_CHECKING([for storm])
if AC_RUN_LOG([$PYTHON -c '
try:
    import storm
except ImportError, e:
    if str(e).find("storm") >= 0:
        raise
except:
    pass
']); then
   AC_MSG_RESULT([yes])
   have_storm=yes
else
   AC_MSG_RESULT([no])
   AC_MSG_WARN([Database output requires storm, database output will be disabled])
   have_storm=no
fi

AM_CONDITIONAL(HAVE_STORM, test x$have_storm = xyes)

AC_CONFIG_FILES([
Makefile
Guilty/Makefile
Guilty/OutputDevs/Makefile
Guilty/Parser/Makefile
])
AC_OUTPUT


