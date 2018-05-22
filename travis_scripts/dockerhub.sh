#!/bin/bash

docker login -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
if [[ $TRAVIS_TAG =~ ^[0-9]+(\.[0-9]+)+$ ]]
then
	docker build -t slidewiki/recommenderservice:$TRAVIS_TAG ./
	docker push slidewiki/recommenderservice:$TRAVIS_TAG
else
	docker build -t slidewiki/recommenderservice:latest-dev ./
	docker push slidewiki/recommenderservice:latest-dev
fi
