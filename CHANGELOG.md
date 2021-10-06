# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project attempts to match the major and minor versions of [stactools](https://github.com/stac-utils/stactools) and increments the patch number as needed.

## [v0.1.6] - 2021-10-06

If not specified, changes were part of [#21](https://github.com/stactools-packages/goes/pull/21).

### Added

- Ability to create a subset of COGs
- Backoff capabilities
- Ability to reproject while making COGs

### Changed

- Refactor GOES items to have multiple products for one observation
- Update stactools dependency to v0.2.3
- Some description and other metadata text

### Fixed

- Volume mounting in Docker containers
- Projection if the xmin value is -999.0 for extreme western shots
- Specific exception is raised if all projection extent values are missing ([#22](https://github.com/stactools-packages/goes/pull/22)])

## [v0.1.5] - 2021-09-13

### Changed

- Update stactools dependency to v0.2.2 ([#19](https://github.com/stactools-packages/goes/pull/19))

### Fixed

- Allow n/a as a ProductionDataSource ([#19](https://github.com/stactools-packages/goes/pull/19))
- Avoid errors when `long_description` is not set ([#19](https://github.com/stactools-packages/goes/pull/19))
- Close hdfpy File to ensure proper cleanup ([#19](https://github.com/stactools-packages/goes/pull/19))

## [v0.1.4] - 2021-09-07

### Changed

- Don't add `eo:bands` to DQF files in MCMIP products ([#17](https://github.com/stactools-packages/goes/pull/17))

## [v0.1.3] - 2021-09-07

### Added

- GOES-specific metadata ([#12](https://github.com/stactools-packages/goes/pull/12))

### Fixed

- Re-added stderr/stdout to cogify ([#15](https://github.com/stactools-packages/goes/pull/15))


## [v0.1.2] - 2021-09-07

### Added

- EO extension for MCMIP items ([#11](https://github.com/stactools-packages/goes/pull/11))
- Raise an error when COGification fails ([#13](https://github.com/stactools-packages/goes/pull/13))

## [v0.1.1] - 2021-09-02

### Added

- More descriptive titles for COG assets ([#9](https://github.com/stactools-packages/goes/pull/9))

## [v0.1.0] - 2021-07-29

Initial release.

### Added

- Everything.

### Deprecated

- Nothing.

### Removed

- Nothing.

### Fixed

- Nothing.
