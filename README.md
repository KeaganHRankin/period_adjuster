# period_adjuster

A small Python utility for adjusting period settings used in a TEMOA DB.

## Overview

This repository contains a single script, [period_adjuster.py](period_adjuster.py), which adjusts the year in the `periods` column by +/- x years for each table in the TEMOA DB. 

## Requirements

- Python 3.12, sqlite3, yaml

## Usage

Run the script from the repository root:

```bash
python period_adjuster.py period_adjuster.yml
```

## Config

The YAML file can include an optional `tables` list to restrict updates to a subset of tables. If `tables` is omitted or left empty, the script updates all tables that contain a `period` column.