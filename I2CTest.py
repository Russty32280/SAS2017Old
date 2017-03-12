import smbus
import time
bus = smbus.SMBus(1)
TempHumidAddress = 0x40
EEPROMAddress = 0x50
LEDAddress = 0x67





def TempRead():
	rawtemp = bus.read_word_data(TempHumidAddress,0xE3)
	#print int(rawtemp)*175.72/65536
	temp = (175.72*rawtemp)/65536 - 46.85
	return temp

def HumidRead():
	rawhumid = bus.read_word_data(TempHumidAddress,0xE5)
	humidity = (125*rawhumid)/65536 - 6
	return humidity

def EEPROMSingleRead():
	data = bus.read_byte(EEPROMAddress)
	return data

def EEPROMSingleWrite():
	bus.write_i2c_block_data(EEPROMAddress,0x00,[0x00, 0xAA])
	return status


def EEPROMMultiRead(startAddress):
	data = bus.read_block_data(EEPROMAddress, startAddress)
	return data
	


while True:
	print TempRead()
	print HumidRead()
	print EEPROMSingleRead()
	print EEPROMSingleWrite()
	time.sleep(.1)
