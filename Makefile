SHELL := /bin/bash
PORT ?= 8080

.PHONY: install build serve clean

install:
	npm install

build:
	npm run build

serve: build
	python3 -m http.server $(PORT) --directory dist

clean:
	rm -rf dist .cache
