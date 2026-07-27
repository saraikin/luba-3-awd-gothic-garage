PYTHON ?= python
ASSET_ARCHIVE ?=
OUTPUT ?= generated

.PHONY: setup bootstrap check generate verify reproduce clean

setup:
	$(PYTHON) -m pip install -r requirements.lock

bootstrap:
	@test -n "$(ASSET_ARCHIVE)" || (echo "Set ASSET_ARCHIVE=/path/to/luba_facade_source_asset_q85.zip" && exit 2)
	$(PYTHON) scripts/bootstrap_asset.py --archive "$(ASSET_ARCHIVE)"

check:
	$(PYTHON) scripts/validate_project.py --config config.json

generate:
	$(PYTHON) scripts/validate_project.py --config config.json --require-asset
	$(PYTHON) scripts/generate_print_package_v2.py --config config.json --output "$(OUTPUT)"

verify:
	$(PYTHON) scripts/validate_project.py --config config.json --require-asset --generated "$(OUTPUT)"

reproduce: bootstrap generate verify

clean:
	rm -rf "$(OUTPUT)"
