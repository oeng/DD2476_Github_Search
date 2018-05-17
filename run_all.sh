#!/usr/bin/env bash

maybe_download_elasticsearch() {
  if [ ! -d elasticsearch-6.2.4 ]; then
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.tar.gz
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.2.4.tar.gz.sha512
    shasum -a 512 -c elasticsearch-6.2.4.tar.gz.sha512
    tar -xzf elasticsearch-6.2.4.tar.gz
    rm -rf elasticsearch-6.2.4.tar.gz
    rm -rf elasticsearch-6.2.4.tar.gz.sha512
  fi
}

maybe_start_crawler() {
  if [ ! -d download_repo ]; then
    echo "Running crawler for $1 minute(s)"
    timeout $1m python3 -m src.Crawler
  else
    echo "Downloaded repos found, delete if you want to run crawler again."
  fi
}

start_elasticsearch() {
  x-terminal-emulator -e ./elasticsearch-6.2.4/bin/elasticsearch
}

run_indexer() {
  if [ ! -d elasticsearch-6.2.4/data/nodes/0 ]; then
    echo "Running indexer, this might take a few minutes..."
    python3 -m src.Indexer
    echo "Indexing done!"
  else
    echo "Index already exists! Delete elasticsearch/data/nodes/0 and rerun script to re-index."
  fi
}

launch_interface() {
  java -jar ./src/GithubSearchInterface/out/artifacts/GithubSearchInterface/GithubSearchInterface.jar
}

usage() {
  echo "USAGE:"
  echo "./run_all <minutes to crawl>"
}

if [[ $# -ne 1 ]]; then
  echo "Error: no crawl time specified"
  usage
  exit
fi

CRAWL_TIME=$1

# Check if elasticsearch directory exists and if not, download it
maybe_download_elasticsearch

# Starting elasticsearch in new process
echo "Starting elasticsearch in new terminal and waiting 15 seconds for elasticsearch to set up"
start_elasticsearch &
sleep 15s

# Run crawler if needed for 5 minutes
maybe_start_crawler "$CRAWL_TIME"

# Run the indexer
run_indexer

# Launch interface as background process
echo "Launching interface..."
launch_interface &
echo "script finished"
