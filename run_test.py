import json
import os
import subprocess
import shutil
import serial

import click


@click.command()
@click.argument('testfile')
@click.argument('expectfile')
def run_test(testfile, expectfile):
    click.echo(f"Running {testfile} and checking results against {expectfile}")
    device_info_json = json.loads(subprocess.check_output("discotool json", shell=True))

    device_location = device_info_json[0]["volumes"][0]["mount_point"]
    device_serial_port = device_info_json[0]["ports"][0]["dev"]

    print(device_info_json[0]["volumes"][0]["mount_point"])
    print(device_info_json[0]["ports"][0]["dev"])

    shutil.copyfile(testfile, os.path.join(device_location, testfile))
    s = serial.Serial(device_serial_port)
    # res = s.read()
    # print(res)

    s.write("\x03".encode())
    s.write("\x04".encode())
    s.write("\x03".encode())

    line = s.readline()
    while not line.startswith(b"Adafruit CircuitPython"):
        print(line)
        line = s.readline()
    print(line)

    # print("sending a")
    # s.write("a".encode())
    print("sending import command")
    s.write(f"import {testfile.replace('.py', '')}\r\n".encode())

    # first line is the import statement so skip it
    line = s.readline()

    line = s.readline()
    output_buffer = ""
    while line != b"finished\r\n":
        print(line)
        output_buffer += line.decode()
        line = s.readline()
    print(line)
    output_buffer += line.decode()

    # change to only newlines
    output_buffer = output_buffer.replace("\r\n", "\n")

    print("output_buffer:")
    print(output_buffer)
    s.close()

    f = open(expectfile, "r")
    expected_results = f.read()
    f.close()

    # maybe there are \r\n's in the one from serial but not the one on the disk?
    if output_buffer != expected_results:
        click.secho("Real output differed from expected results!", fg="red")
        click.echo("Expected Output:")
        click.echo(expected_results.encode())
        click.echo("------------")
        click.echo("Actual Output:")
        click.echo(output_buffer.encode())
        click.echo("------------")
    else:
        click.secho("Test Passed!", fg="green")
    return


if __name__ == '__main__':
    run_test()
