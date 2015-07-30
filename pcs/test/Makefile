python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python2 --version 2>&1)))
python_version_major := $(word 1,${python_version_full})
python_version_minor := $(word 2,${python_version_full})
python_version_major_minor := ${python_version_major}.${python_version_minor}

ifneq ($(python_version_major_minor),2.6)
  pyunit_flags = -f
endif

ifndef $(PYTHON)
	PYTHON = python2
endif

test:
	$(PYTHON) test_utils.py ${pyunit_flags}
	$(PYTHON) test_corosync_conf.py ${pyunit_flags}
	$(PYTHON) test_cluster.py ${pyunit_flags}
	$(PYTHON) test_resource.py ${pyunit_flags}
	$(PYTHON) test_rule.py ${pyunit_flags}
	$(PYTHON) test_constraints.py ${pyunit_flags}
	$(PYTHON) test_stonith.py ${pyunit_flags}
	$(PYTHON) test_properties.py ${pyunit_flags}
	$(PYTHON) test_acl.py ${pyunit_flags}
