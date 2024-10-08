#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Cleaning up background processes..."
    pkill -P $$
}

# Trap EXIT signal to run the cleanup function
trap cleanup EXIT

promtail -config.file=config-promtail.yml &
python3 api.py &

wait
