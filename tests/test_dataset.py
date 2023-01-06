import unittest

from h5py import File

from stactools.goes import Dataset
from stactools.goes.file_name import ABIL2FileName
from tests import CMIP_FILE_NAME, test_data


class DatasetTest(unittest.TestCase):
    def test_spatial_resolution(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        file_name = ABIL2FileName.from_href(path)
        with open(path, "rb") as f:
            with File(f) as nc:
                dataset = Dataset.from_nc(file_name, nc)
                self.assertEqual(dataset.global_attributes.spatial_resolution_km, 0.5)
