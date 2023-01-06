#!/usr/bin/env python3

"""Create the repository examples.

Before creating examples, make sure the test suite has been run -- this will
download an example HDF file to `tests/data-files/external`.
"""

import shutil
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import DefaultDict, Dict

from pystac import Asset, CatalogType, Collection, Extent
from pystac.summaries import Summarizer
from stactools.core import copy

from stactools.goes import stac

root = Path(__file__).parents[1]
examples = root / "examples"
external = root / "tests" / "data-files" / "external"
paths = list(external.glob("*L2-CMIP*.nc"))

items = list()
shutil.rmtree(examples, ignore_errors=True)
with TemporaryDirectory() as temporary_directory:
    for i, path in enumerate(paths):
        if "CMIPF" in str(path):
            print(f"[{i + 1}/{len(paths)}] Creating item for {path}")
            item = stac.create_item_from_href(str(path))
        else:
            print(f"[{i + 1}/{len(paths)}] Creating COGs and item for {path}")
            item = stac.create_item_from_href(
                str(path), cog_directory=temporary_directory
            )

        items.append(item)

    extent = Extent.from_items(items)
    collection = Collection(
        "goes-cmi",
        "An example collection for GOES CMI data",
        extent=extent,
    )
    collection.add_items(items)
    collection.normalize_hrefs(str(examples))
    item_assets: DefaultDict[str, Dict[str, Asset]] = defaultdict(dict)
    for item in collection.get_items():
        for key, asset in item.get_assets().items():
            if asset.media_type == "application/netcdf":
                item_assets[item.id][key] = asset
                del item.assets[key]
    copy.move_all_assets(collection)
    for item_id, assets in item_assets.items():
        item = collection.get_item(item_id)
        for key, asset in assets.items():
            item.assets[key] = asset
    collection.make_all_asset_hrefs_relative()

summaries = Summarizer().summarize(collection)
collection.summaries = summaries
collection.save(CatalogType.SELF_CONTAINED)
