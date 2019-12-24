# SPS30 PM Sensor I2C Driver for Python3

SPS30 is a Particulate Matter sensor manufactured by Sensirion. It is capable to measure 10 different value of particles. With this driver, you can use SPS30 with Python3 over I2C.

## Dependencies
Only smbus2 other than Python. 

## Installation
```bash
pip3 install sps30
```

## Usage
From command line;
```bash
run-sps30
```
From Python script;
```python
from sps30 import SPS30
from time import sleep

sps = SPS30(1)

if sps.read_article_code() == sps.ARTICLE_CODE_ERROR:
    raise Exception("ARTICLE CODE CRC ERROR!")
else:
    print("ARTICLE CODE: " + str(sps.read_article_code()))

if sps.read_device_serial() == sps.SERIAL_NUMBER_ERROR:
    raise Exception("SERIAL NUMBER CRC ERROR!")
else:
    print("DEVICE SERIAL: " + str(sps.read_device_serial()))

sps.set_auto_cleaning_interval(seconds) # default 604800, set 0 to disable auto-cleaning

sps.device_reset() # device has to be powered-down or reset to check new auto-cleaning interval

if sps.read_auto_cleaning_interval() == sps.AUTO_CLN_INTERVAL_ERROR: # or returns the interval in seconds
    raise Exception("AUTO-CLEANING INTERVAL CRC ERROR!")
else:
    print("AUTO-CLEANING INTERVAL: " + str(sps.read_auto_cleaning_interval()))

sps.start_measurement()

while not sps.read_data_ready_flag():
    print("New Measurement is not available!")
    if sps.read_data_ready_flag() == sps.DATA_READY_FLAG_ERROR:
        raise Exception("DATA-READY FLAG CRC ERROR!")

if sps.read_measured_values() == sps.MEASURED_VALUES_ERROR:
    raise Exception("MEASURED VALUES CRC ERROR!")
else:
    print ("PM1.0 Value in µg/m3: " + str(sps.dict_values['pm1p0']))
    print ("PM2.5 Value in µg/m3: " + str(sps.dict_values['pm2p5']))
    print ("PM4.0 Value in µg/m3: " + str(sps.dict_values['pm4p0']))
    print ("PM10.0 Value in µg/m3: " + str(sps.dict_values['pm10p0']))
    print ("NC0.5 Value in 1/cm3: " + str(sps.dict_values['nc0p5']))    # NC: Number of Concentration 
    print ("NC1.0 Value in 1/cm3: " + str(sps.dict_values['nc1p0']))
    print ("NC2.5 Value in 1/cm3: " + str(sps.dict_values['nc2p5']))
    print ("NC4.0 Value in 1/cm3: " + str(sps.dict_values['nc4p0']))
    print ("NC10.0 Value in 1/cm3: " + str(sps.dict_values['nc10p0']))
    print ("Typical Particle Size in µm: " + str(sps.dict_values['typical']))	

sps.stop_measurement()

sps.start_fan_cleaning() # enables fan-cleaning manually for 10 seconds (referred by datasheet)
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
