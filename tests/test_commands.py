import os
from tempfile import TemporaryDirectory

import pystac

from stactools.testing import CliTestCase

from stactools.goes.commands import create_goes_command
from tests import test_data, CMIP_FILE_NAME, MCMIP_FILE_NAME


class CreateItemTest(CliTestCase):
    def create_subcommand_functions(self):
        return [create_goes_command]

    def test_create_item(self):
        path = test_data.get_external_data(CMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
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
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
            cog_data = item.assets["CMI"]
            self.assertTrue(os.path.exists(cog_data.href))
            cog_dqf = item.assets["DQF"]
            self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()

    def test_create_item_with_cogify_multiband(self):
        path = test_data.get_external_data(MCMIP_FILE_NAME)
        with TemporaryDirectory() as tmp_dir:
            args = ["goes", "create-item", "--cogify", path, tmp_dir]
            result = self.run_command(args)
            self.assertEqual(result.exit_code, 0)
            jsons = [p for p in os.listdir(tmp_dir) if p.endswith('.json')]
            self.assertEqual(len(jsons), 1)
            path = os.path.join(tmp_dir, jsons[0])
            item = pystac.read_file(path)
            for i in range(1, 17):
                cog_data = item.assets[f"CMI_C{i:02d}"]
                self.assertTrue(os.path.exists(cog_data.href))
                cog_dqf = item.assets[f"DQF_C{i:02d}"]
                self.assertTrue(os.path.exists(cog_dqf.href))
        item.validate()
