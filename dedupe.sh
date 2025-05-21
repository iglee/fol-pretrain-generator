#!/bin/bash

# Check if a filename is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

# Check if the file exists
if [ ! -f "$1" ]; then
  echo "File $1 does not exist!"
  exit 1
fi

# Deduplicate the file by sorting and removing duplicates
sort "$1" | uniq > "$1.deduped"

# Print a message with the location of the deduplicated file
echo "File has been deduplicated and saved as $1.deduped"
