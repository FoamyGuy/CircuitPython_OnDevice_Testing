import json
import shutil
import subprocess
import unittest
import yaml
from pathlib import Path
from serial import Serial
from typing import Dict, Tuple, Union

THIS = Path(__file__)
BASE = THIS.parent.parent
YAML = BASE / "tests.yaml"
SCRIPTS = BASE / "scripts"
EXPECT = BASE / "expected"

CR = "\r"
LF = "\n"
CRLF = CR + LF


class OnDeviceTest(unittest.TestCase):
    def get_files(self, arg: Union[str, Dict[str, str]]) -> Tuple[Path, Path]:
        """
        Get script and expected output files for a test.
        Input could be a string (test name) or dict (info about the test)
        """

        if isinstance(arg, str):
            script = SCRIPTS / (arg + ".py")
            expect = EXPECT / arg
        
        elif isinstance(arg, dict):
            script = Path(arg["script"]).resolve()
            self.assertTrue(script.name.endswith(".py"), "Script should be a .py file")
            expect = Path(arg["expect"]).resolve()

        else:
            self.fail(f"{arg=!r} should have been a str or dict.")

        return script, expect

    def run_script(self, board: str, script: Path, expect: Path):
        """
        Run a single script and check if it output matches expectation.
        """

        # find device's information
        found = False
        for info in self.boards:
            if info["name"] == board or board == "any":
                found = True
                break
        if not found:
            self.fail(f"Did not find {board!r}")

        mount = Path(info["volumes"][0]["mount_point"])
        serial = Serial(info["ports"][0]["dev"])

        # shutil does not work on Path until 3.8, lets str()
        target = mount / script.name
        shutil.copy(str(script), str(target))

        # restart the board
        line = ""
        serial.write(bytes([3, 4, 3]))
        while not line.startswith(b"Adafruit CircuitPython"):
            line = serial.readline()

        # copy script on board, execute, capture its output
        script_name = script.name[:-3]  # remove '.py'
        serial.write(f"import {script_name}{CRLF}".encode())
    
        line = output = ""
        while line != f"finished{CRLF}".encode():
            line = serial.readline()
            output += line.decode()
        output = output.replace(CRLF, LF)

        # check if it matches
        with expect.open("r") as f:
            expected_output = f.read()
        self.assertEqual(expected_output, output, "Output doesnt match.")

    def test_all(self):
        """
        Parse the YAML file and execute every test in it.
        """

        # grab information once, instead of once per test
        self.boards = None
        try:
            self.boards = json.loads(
                subprocess.check_output(
                    "discotool json",
                    shell=True
                )
            )
        except:
            pass

        if self.boards is None:
            self.fail("Could not find any device, aborting...")

        with YAML.open("r") as f:
            test_suite = yaml.safe_load(f.read())

        for board, info in test_suite:
            with self.subTest(board=board):
                tests = info.get("tests")
                if tests is None:
                    self.fail("Missing test list")

                for test in tests:
                    script, expect = self.get_files(test)
                    with self.subTest(script=script.name[:-3]):
                        self.run_script(board, script, expect)


if __name__ == "__main__":
    """
    Entrypoint of the program. Will cause execution of our tests.
    """
    unittest.main()