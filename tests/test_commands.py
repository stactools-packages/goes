import os
from tempfile import TemporaryDirectory

import pystac
from stactools.testing import CliTestCase

from stactools.goes.commands import create_goes_command
from tests import CMIP_FILE_NAME, MCMIP_FILE_NAME, test_data


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_goes_command]

    def test_create_item(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
        item.validate()

    def test_create_item_with_cogify(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", "--cogify", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.Item.from_file(path)

            cog_data = item.assets["CMIP_C02"]
            self.assertTrue(os.path.exists(cog_data.href))
            cog_dqf = item.assets["CMIP_C02_DQF"]
            self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()

    def test_create_item_with_cogify_multiband(self):
        path = test_data.get_external_data(MCMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", "--cogify", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith(".json")]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.Item.from_file(path)
            for i in range(1, 17):
                cog_data = item.assets[f"CMI_C{i:02d}_2km"]
                self.assertTrue(os.path.exists(cog_data.href))
                cog_dqf = item.assets[f"CMI_C{i:02d}_DQF_2km"]
                self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()
