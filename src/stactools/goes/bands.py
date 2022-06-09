from pystac.extensions.eo import Band

ABI_CHANNEL_BANDS = {
    1: Band.create(
        common_name="blue",
        name="ABI Band 1",
        description="Daytime aerosol over land, coastal water mapping",
        center_wavelength=0.47,
    ),
    2: Band.create(
        common_name="red",
        name="ABI Band 2",
        description="Daytime clouds, fog, insolation, winds",
        center_wavelength=0.64,
    ),
    3: Band.create(
        common_name="nir09",
        name="ABI Band 3",
        description="Daytime vegetation, burn scar, aerosol over water, winds",
        center_wavelength=0.87,
    ),
    4: Band.create(
        common_name="cirrus",
        name="ABI Band 4",
        description="Daytime cirrus cloud",
        center_wavelength=1.38,
    ),
    5: Band.create(
        common_name="swir16",
        name="ABI Band 5",
        description="Daytime cloud-top phase and particle size, snow",
        center_wavelength=1.61,
    ),
    6: Band.create(
        common_name="swir22",
        name="ABI Band 6",
        description=("Daytime land, cloud properties, particle size, vegetation, snow"),
        center_wavelength=2.25,
    ),
    7: Band.create(
        name="ABI Band 7",
        description="Surface and cloud, fog at night, fire, winds",
        center_wavelength=3.89,
    ),
    8: Band.create(
        name="ABI Band 8",
        description="High-level atmospheric water vapor, winds, rainfall",
        center_wavelength=6.17,
    ),
    9: Band.create(
        name="ABI Band 9",
        description="Midlevel atmospheric water vapor, winds, rainfall",
        center_wavelength=6.93,
    ),
    10: Band.create(
        name="ABI Band 10",
        description="Lower-level water vapor, winds, and silicon dioxide",
        center_wavelength=7.34,
    ),
    11: Band.create(
        name="ABI Band 11",
        description=(
            "Total water for stability, cloud phase, " "dust, silicon dioxide, rainfall"
        ),
        center_wavelength=8.44,
    ),
    12: Band.create(
        name="ABI Band 12",
        description="Total ozone, turbulence, winds",
        center_wavelength=9.61,
    ),
    13: Band.create(
        name="ABI Band 13", description="Surface and clouds", center_wavelength=10.33
    ),
    14: Band.create(
        name="ABI Band 14",
        description="Imagery, sea surface temperature, clouds, rainfall",
        center_wavelength=11.19,
    ),
    15: Band.create(
        name="ABI Band 15",
        description="Total water, volcanic ash, sea surface temperature",
        center_wavelength=12.27,
    ),
    16: Band.create(
        name="ABI Band 16",
        description="Air temperature, cloud heights",
        center_wavelength=13.27,
    ),
}


# Resolution of channels in meters
def get_channel_resolution(channel: int) -> int:
    if channel == 1 or channel == 3 or channel == 5:
        return 1000
    elif channel == 2:
        return 500
    else:
        return 2000
