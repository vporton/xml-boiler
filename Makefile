.PHONY: all docs

all: docs

docs: build/html/index.html build/html/syntax.css

build/html/%.html: xmlboiler/doc/%.html
	mkdir -p build/html
#	xsltproc -o $@ xmlboiler/core/data/scripts/section.xslt $<
	PYTHONPATH=. ./bin/boiler -i $< -o $@ c -t http://www.w3.org/1999/xhtml -n error

build/html/syntax.css:
	pygmentize -f html -S colorful > $@