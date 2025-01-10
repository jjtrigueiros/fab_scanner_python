# fab_scanner_python

A Python real-time card identification system using classic computer vision and perceptual hashing made for [Flesh and Blood](https://fabtcg.com/) (work in progress!)

This project can be used as a CLI tool or an Android app.

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for development but it is not required for installation.
Install the project using `pip install -e .` or `uv pip install -e .`
Read the help page for the CLI tool with `fabscan --help` or `uv run fabscan --help`


Commands are subject to change. At time of writing,
- download: pulls all the images from fabtcg
- match: scans a single image and outputs the best match
- scan: connects to the first detected camera device and continually scans/matches cards
