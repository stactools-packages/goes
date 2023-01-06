# stactools-goes

[![PyPI](https://img.shields.io/pypi/v/stactools-goes)](https://pypi.org/project/stactools-goes/)

- Name: goes
- Package: `stactools.goes`
- [stactools-goes on PyPI](https://pypi.org/project/stactools-goes/)
- Owner: @gadomski
- [Dataset homepage](https://www.goes.noaa.gov/)
- STAC extensions used:
  - [eo](https://github.com/stac-extensions/eo/)
  - [processing](https://github.com/stac-extensions/processing/)
  - [projection](https://github.com/stac-extensions/projection/)
  - [raster](https://github.com/stac-extensions/raster/)
- Extra fields:
  - `goes:system-environment`: The environment, e.g. operational real-time, operational test, or simulated data
  - `goes:image-type`: Full disk, mesoscale, or CONUS data
  - `goes:processing-level`: The processing level of the data
  - `goes:mesoscale-image-number`: The image number of the mesoscale data (1 or 2)
- [Browse the example in human-readable form](https://radiantearth.github.io/stac-browser/#/external/raw.githubusercontent.com/stactools-packages/goes/main/examples/collection.json)

A short description of the package and its usage.

## STAC Examples

- [Collection](./examples/collection.json)
- [Item](./examples/OR_ABI-L2-M1-M6_G16_s20211231619248/OR_ABI-L2-M1-M6_G16_s20211231619248.json)

## Installation

```shell
pip install stactools-goes
```

## Command-line Usage

```shell
stac goes create-item source destination
```

Use `stac goes --help` to see all subcommands and options.

## Contributing

We use [pre-commit](https://pre-commit.com/) to check any changes.
To set up your development environment:

```shell
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

To check all files:

```shell
pre-commit run --all-files
```

To run the tests:

```shell
pytest -vv
```
