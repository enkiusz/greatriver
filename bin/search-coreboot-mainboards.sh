#!/bin/sh

fetch-coreboot-mobos.py  | jq '.[] | [.vendor,.model] | "\(.[0]) \(.[1])"'  | xargs prodsearch.py --category 77808 --category 4228 --category 491
