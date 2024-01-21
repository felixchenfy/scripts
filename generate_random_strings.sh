#!/bin/bash

# Function to generate a random 8-character string
generate_random_string() {
  cat /dev/urandom | tr -dc 'a-zA-Z' | fold -w 8 | head -n 1
}

# Generate and print 10 random strings
for i in {1..10}; do
  generate_random_string
done
