"""
Copyright (C) 2021 Red Hat, Inc. (https://github.com/Commonjava/mrrc-uploader)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json
import os
import shutil

import mrrc.utils.archive as archive
from mrrc.pkgs.npm import (
    scan_for_version,
    gen_package_metadata_file,
)
from tests.base import BaseMRRCTest


class NPMMetadataTest(BaseMRRCTest):

    def test_scan_for_version(self):
        version_json_file_path = 'tests/input/code-frame_7.14.5.json'
        version = scan_for_version(version_json_file_path)
        self.assertEqual('@babel/code-frame', version.get('name'))
        self.assertEqual('7.14.5', version.get('version'))
        self.assertEqual('MIT', version.get('license'))
        self.assertEqual(
            'https://registry.npmjs.org/@babel/code-frame/-/code-frame-7.14.5.tgz',
            version.get('dist')['tarball']
            )
        self.assertEqual(4, version.get('dist')['fileCount'])

    def test_gen_package_meta_file(self):
        temp_root = os.path.join(self.tempdir, 'tmp_tgz')
        os.mkdir(temp_root)
        tarball_test_path = 'tests/input/kogito-tooling-workspace-0.9.0-3.tgz'
        package_name_path, valid_paths = archive.extract_npm_tarball(
            tarball_test_path, temp_root, True
            )
        version = scan_for_version(valid_paths[1])
        gen_package_metadata_file(version, temp_root)

        npm_meta_file = os.path.join(temp_root, '@redhat/kogito-tooling-workspace/package.json')
        if not os.path.isfile(npm_meta_file):
            self.fail('package.json is not generated correctly!')
        with open(npm_meta_file, encoding='utf-8') as verified_package_meta_file:
            verified_package_meta_data = json.load(verified_package_meta_file)
        name = verified_package_meta_data.get('name')
        self.assertEqual('@redhat/kogito-tooling-workspace', name)
        _license = verified_package_meta_data.get('license')
        self.assertEqual('Apache-2.0', _license)
        repo = verified_package_meta_data.get('repository')
        self.assertEqual('git', repo['type'])
        self.assertEqual('https://github.com/kiegroup/kogito-tooling.git', repo['url'])

        shutil.rmtree(temp_root)
