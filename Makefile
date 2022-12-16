PY_SRCS = $(wildcard server/*.py)
PY_VERSION = $(shell bash ./utils/get_py_version.sh)
PY_WHL = k6webserver-$(PY_VERSION)-py3-none-any.whl

################################################################################

.PHONY: default
default: help

.PHONY: help
help:
	@echo "TARGETS"
	@echo "    help         print this help text."
	@echo "    clean        Clean up build artifacts."
	@echo "    pybuild      Build python package."
	@echo ""
	@echo "PY_VERSION = $(PY_VERSION)"

.PHONY: clean
clean:
	rm -rf dist k6webserver.egg-info build

.PHONY: pybuild
pybuild: dist/$(PY_WHL)

################################################################################

dist/$(PY_WHL): $(PY_SRCS) setup.py
	@python ./setup.py bdist_wheel
