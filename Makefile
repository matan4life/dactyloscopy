# The only place a "docker run" invocation is written. A command typed by hand
# is a command that can differ from the one that produced a number.

IMAGE ?= dactyloscopy:dev
LABDATA ?=
FVC_DB1_B ?=

# Docker on Windows takes Windows paths. Under Git Bash and MSYS a POSIX path
# in a "-v" argument is rewritten before docker sees it: "/work" becomes
# "C:/Program Files/Git/work", and the mount silently lands somewhere else.
# MSYS_NO_PATHCONV=1 turns that rewriting off; docs/container.md records what
# the failure looks like without it.
DOCKER := MSYS_NO_PATHCONV=1 docker

# "pwd -W" prints the Windows form of the current directory under MSYS and
# fails elsewhere, where plain pwd is already right.
REPO := $(shell pwd -W 2>/dev/null || pwd)

# cygpath -m gives the Windows path with forward slashes, which docker accepts
# and a shell does not mangle. Absent cygpath, LABDATA is passed through.
LABDATA_HOST := $(shell cygpath -m "$(LABDATA)" 2>/dev/null || echo "$(LABDATA)")
FVC_DB1_B_HOST := $(shell cygpath -m "$(FVC_DB1_B)" 2>/dev/null || echo "$(FVC_DB1_B)")

DATA_MOUNTS := -v "$(LABDATA_HOST)/raw:/data/raw:ro" -v "$(LABDATA_HOST)/derived:/data/derived"
REPO_MOUNT := -v "$(REPO):/work"

.DEFAULT_GOAL := help
.PHONY: help image shell test check-tools verify

help: ## List the targets
	@echo "Targets:"
	@grep -E '^[a-z][a-z-]*:.*## ' $(MAKEFILE_LIST) | sed 's/:.*## /|/' | awk -F'|' '{ printf "  %-12s %s\n", $$1, $$2 }'
	@echo ""
	@echo "Variables:"
	@echo "  IMAGE        image name and tag (currently $(IMAGE))"
	@echo "  LABDATA      root of the data mounted into the container; required by shell,"
	@echo "               and by verify if the corpus is to be checked"
	@echo "  FVC_DB1_B    directory of FVC2002 Db1_b images; required by check-tools"

image: ## Build the image and print its digest
	$(DOCKER) build -t "$(IMAGE)" .
	@echo ""
	@echo "image id:"
	@docker image inspect "$(IMAGE)" --format '{{.Id}}'
	@echo "base, as pinned in the Dockerfile:"
	@grep '^FROM' Dockerfile

shell: ## Interactive session in the container, with the data mounted
	@if [ -z "$(LABDATA)" ]; then \
	  echo "LABDATA is not set, so nothing was started."; \
	  echo ""; \
	  echo "It names the root the data is mounted from, and the container"; \
	  echo "expects this layout under it:"; \
	  echo ""; \
	  echo "  \$$LABDATA/raw        mounted read-only at /data/raw"; \
	  echo "  \$$LABDATA/derived    mounted read-write at /data/derived"; \
	  echo ""; \
	  echo "Set it for one command:"; \
	  echo ""; \
	  echo "  LABDATA=/path/to/labdata make shell"; \
	  echo ""; \
	  echo "or export it in the shell. See docs/data.md for what may live there."; \
	  exit 1; \
	fi
	$(DOCKER) run --rm -it $(REPO_MOUNT) $(DATA_MOUNTS) -w /work "$(IMAGE)" bash

# There is a suite now, so pytest's exit 5 — it collected nothing — is no
# longer the expected state and is not swallowed. It would mean the mount, the
# working directory or the suite itself is wrong, and that is a failure worth
# stopping on rather than a message.
test: ## Run pytest in the container; needs no data
	$(DOCKER) run --rm $(REPO_MOUNT) -w /work "$(IMAGE)" python -m pytest

# LABDATA is optional here, and the difference is reported rather than hidden:
# without it the corpus checks are printed as not run, with it every listed
# digest is verified. quality/REF-014 decision 4 requires the skip to be
# visible, because a skipped check reported as a pass is the failure the whole
# mechanism exists to remove.
verify: ## Verify every manifest against what it names; LABDATA adds the corpus
	@if [ -n "$(LABDATA)" ]; then 	  $(DOCKER) run --rm $(REPO_MOUNT) -v "$(LABDATA_HOST)/raw:/data/raw:ro" 	    -w /work -e LABDATA=/data "$(IMAGE)" bash scripts/verify_manifests.sh; 	else 	  $(DOCKER) run --rm $(REPO_MOUNT) -w /work "$(IMAGE)" 	    bash scripts/verify_manifests.sh; 	fi

check-tools: ## Verify the tools in the image against manifests/MAN-tools.v2.json
	@if [ -z "$(FVC_DB1_B)" ]; then \
	  echo "FVC_DB1_B is not set, so nothing was checked."; \
	  echo ""; \
	  echo "It names the directory holding the FVC2002 Db1_b images, which the"; \
	  echo "fixture in manifests/MAN-tools.v2.json was recorded against:"; \
	  echo ""; \
	  echo "  make check-tools FVC_DB1_B=/path/to/FVC2002/Dbs/Db1_b"; \
	  echo ""; \
	  echo "The directory is mounted read-only and no layout under LABDATA is"; \
	  echo "assumed: that is not decided yet."; \
	  exit 1; \
	fi
	$(DOCKER) run --rm $(REPO_MOUNT) -v "$(FVC_DB1_B_HOST):/fixture:ro" -w /work "$(IMAGE)" bash scripts/check_tools.sh /fixture
