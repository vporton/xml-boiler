.PHONY: all docs

all: docs

docs: build/html/index.html

build/html/%.html: doc/%.html
	xsltproc -o $@ xmlboiler/core/data/scripts/section.xslt $<
