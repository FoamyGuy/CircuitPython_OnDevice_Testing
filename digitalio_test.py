
import board
import digitalio

dio_13 = digitalio.DigitalInOut(board.D13)
dio_13.direction = digitalio.Direction.INPUT
dio_13.pull = digitalio.Pull.DOWN

dio_12 = digitalio.DigitalInOut(board.D12)
dio_12.direction = digitalio.Direction.OUTPUT

dio_11 = digitalio.DigitalInOut(board.D11)
dio_11.direction = digitalio.Direction.INPUT
dio_11.pull = digitalio.Pull.UP

dio_10 = digitalio.DigitalInOut(board.D10)
dio_10.direction = digitalio.Direction.INPUT
dio_10.pull = digitalio.Pull.DOWN

print("setting pin 12 HIGH")
dio_12.value = True
print("pin 12 is connected to pin 13 and the onboard LED so the LED should turn on")
print(f"pin 13 value: {dio_13.value} (expected True)")

print(f"pin 11 value: {dio_11.value} (expected False)")
print(f"pin 10 value: {dio_10.value} (expected True)")

print("finished")
