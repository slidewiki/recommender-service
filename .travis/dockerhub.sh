#!/bin/bash

echo $DOCKER_PASSWORD | docker login -u="$DOCKER_USERNAME" --password-stdin

if [[ $TRAVIS_TAG =~ ^[0-9]+(\.[0-9]+)+$ ]]
then
	docker build --build-arg BUILD_ENV=travis -t slidewiki/recommenderservice:$TRAVIS_TAG ./
	docker push slidewiki/recommenderservice:$TRAVIS_TAG
else
	docker build --build-arg BUILD_ENV=travis -t slidewiki/recommenderservice:latest-dev ./
	docker push slidewiki/recommenderservice:latest-dev
fi
