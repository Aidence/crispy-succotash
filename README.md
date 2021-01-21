# Crispy Succotash
Crispy Succotash is an RSS feed scraper tool built for testing and hiring purposes.

It's a simple application which supports the following features:
* User account creation and login
* Different users should be able to see other user's RSS feeds and bookmark them
* Support to follow multiple feeds. A list of feeds can be found at [this feed list](https://www.uen.org/feeds/lists.shtml)
* Ability to add Markdown based comments to the feed items and see other user's comments
* It should be able to fetch up to 5 feeds at once

## Installation

1. Install [Docker](https://docs.docker.com/installation/) and [Docker Compose](https://docs.docker.com/compose/install/)
2. Run it

  ```shell
  make up
  ```

That's it! :) The project will be available on port 8000 (http://localhost:8000).

## Other commands

  ```shell
  # build docker image
  make build
  # run tests
  make test
  # ssh into container
  make ssh
  ```
