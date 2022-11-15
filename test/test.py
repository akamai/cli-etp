# Copyright 2022 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module replaces the old test.bash script
Tested with nose2:

```bash

# Optional
EDGERC_SECTION=mysection
# End Optional

cd test
nose2 -v
open report.html
```
"""

import unittest
import subprocess
import shlex
import time
from pathlib import Path
import collections
import tempfile
import os
import random
import re

# Global variables
encoding = 'utf-8'


class CliETPTest(unittest.TestCase):
    seed = 0
    testdir = None
    maindir = None

    def setUp(self):
        self.testdir = Path(__file__).resolve().parent
        self.maindir = Path(__file__).resolve().parent.parent
        self.seed = random.randint(10000, 99999)

    def cli_command(self, *args):
        command = shlex.split(f'python3 {self.maindir}/bin/akamai-etp')
        if os.environ.get('EDGERC_SECTION'):
            command.extend(["--section", os.environ['EDGERC_SECTION']])
        command.extend(*args)
        print("\nCOMMAND: ", " ".join(command))
        return command

    def cli_run(self, *args):
        cmd = subprocess.Popen(self.cli_command(str(a) for a in args), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return cmd

    def line_count(filename):
        count = 0
        with open(filename) as f:
            while next(f, False):
                count += 1
        return count

    def duplicate_count(filename):
        total_count = 0
        with open(filename) as infile:
            counts = collections.Counter(line.strip() for line in infile)
        for line, count in counts.most_common():
            if count > 1:
                print(f"DUPLICATE[{count}] {line}")
                total_count += 1
        return total_count


class TestEvents(CliETPTest):

    after = int(time.time() - 15 * 60)
    before = int(time.time())

    def test_event_threat(self):
        """
        Fetch threat events
        """
        cmd = self.cli_run("event", "threat", "--start", self.after, "--end", self.before)
        stdout, stderr = cmd.communicate(timeout=60)
        events = stdout.decode(encoding)
        event_count = len(events.splitlines())
        self.assertGreater(event_count, 0, "We expect at least one threat event")
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')

    def test_event_aup(self):
        """
        Fetch AUP events
        """
        cmd = self.cli_run("event", "aup", "--start", self.after, "--end", self.before)
        stdout, stderr = cmd.communicate(timeout=120)
        events = stdout.decode(encoding)
        event_count = len(events.splitlines())
        self.assertGreater(event_count, 0, "We expect at least one AUP event")
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')

    def test_event_aup_file(self):
        """
        Fetch AUP events, export as a file
        """
        output_handle, output_filename = tempfile.mkstemp()
        try:
            cmd = self.cli_run("event", "aup", "--start", self.after, "--end", self.before, '--output', output_filename)
            stdout, stderr = cmd.communicate(timeout=120)
            self.assertEqual(cmd.returncode, 0, 'return code must be 0')
            line_count = TestCliETP.line_count(output_filename)
            print(f"Output contains {line_count} lines")
            duplicate_count = CliETPTest.duplicate_count(output_filename)
            self.assertGreater(line_count, 0, "We expect at least a few events")
            print(f"We found {duplicate_count} duplicates")
            self.assertEqual(duplicate_count, 0)

        finally:
            if os.path.isfile(output_filename):
                os.remove(output_filename)


class TestCliETP(CliETPTest):

    def test_no_edgerc(self):
        """
        Call CLI with a bogus edgerc file, help should be displayed.
        """
        cmd = self.cli_run('-e', 'file_not_exist')
        stdout, stderr = cmd.communicate()
        output = stdout.decode(encoding)
        self.assertIn("usage: akamai etp", output)
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')

    def test_cli_version(self):
        """
        Ensure version of the CLI is displayed
        """
        cmd = self.cli_run('version')
        stdout, stderr = cmd.communicate()
        self.assertRegex(stdout.decode(encoding), r'[0-9]+\.[0-9]+\.[0-9]+\n', 'Version should be x.y.z')
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')


class TestListETP(CliETPTest):

    listid = None

    """
    Create a list
    """
    def setUp(self):
        super().setUp()
        cmd = self.cli_run('list', 'create', f'clietp_list_{self.seed}', "Created by test/test.py", 4)
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            print(stdout, stderr)

        self.listid = stdout
        regex = r" (\d+) "
        matches = re.findall(regex, stdout.decode())
        self.assertEqual(len(matches), 1, 'A list ID must be displayed after the command akamai etp list create ...')
        self.listid = int(matches[0])
        print("ListID=", self.listid)
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')

    def tearDown(self):
        if self.listid:
            cmd = self.cli_run('list', 'delete', self.listid)
            stdout, stderr = cmd.communicate()
            if cmd.returncode != 0:
                print("ERROR cli_run:", stdout, stderr)
            self.assertEqual(cmd.returncode, 0, 'return code must be 0')

    """
    TODO: add a create and remove list once implemented in the cli
    """
    def test_add100_list(self):

        test_fqdns = list("testhost-{}-{}.cli-etp.unittest".format(i, self.seed) for i in range(100))

        cmd = self.cli_run('list', 'add_item', self.listid, *test_fqdns)
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            print(stdout, stderr)
        self.assertEqual(cmd.returncode, 0, 'add 100 items sub-operation: return code must be 0')

        cmd = self.cli_run('list', 'remove_item', self.listid, *test_fqdns)
        stdout, stderr = cmd.communicate()
        if cmd.returncode != 0:
            print("ERROR with the command ", cmd.args, stdout, stderr)
        self.assertEqual(cmd.returncode, 0, 'remove 100 items sub-operation: return code must be 0')

    def test_get_lists(self):
        """
        Get the security lists configured in the tenant
        """
        cmd = self.cli_run('list', 'get')
        stdout, stderr = cmd.communicate()
        output = stdout.decode(encoding)
        line_count = len(output.splitlines())
        print(line_count)
        self.assertGreater(line_count, 0, "We expect at least one list to be on this tenant/config_id")
        self.assertEqual(cmd.returncode, 0, 'return code must be 0')


if __name__ == '__main__':
    unittest.main()
