import os.path

import click

from stactools.goes import cog, stac


def create_goes_command(cli):
    @cli.group("goes", short_help="Command for working with GOES data")
    def goes():
        pass

    @goes.command(
        "create-item", short_help="Creates a STAC item from a GOES netcdf file"
    )
    @click.argument("href")
    @click.argument("destination")
    @click.option(
        "-c",
        "--cogify",
        is_flag=True,
        help="Convert the netcdf into COGs. COG Asset HREFs will be local paths",
    )
    def create_item(href, destination, cogify):
        """Creates a STAC item from a GOES netcdf file.

        If `--cogify` is provided, will produce two COGs, one for the data and
        one for the data quality field.
        """
        if cogify:
            cogs = cog.cogify(href, destination)
        else:
            cogs = {}
        item = stac.create_item([stac.ProductHrefs(nc_href=href, cog_hrefs=cogs)])
        path = os.path.join(destination, f"{item.id}.json")
        item.set_self_href(path)
        item.validate()
        item.save_object()

    return goes
