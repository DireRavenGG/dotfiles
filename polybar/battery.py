from bluetooth_battery import BatteryStateQuerier, BatteryQueryError, BluetoothError
try:
    query = BatteryStateQuerier("20:78:CD:22:EB:9F")  # Can raise BluetoothError when autodetecting port


    
    print(str(query))                                        # Can raise BluetoothError when device is down or port is wrong
                                                      # Can raise BatteryQueryError when the device is unsupported
except BluetoothError as e:
    # Handle device is offline
    print("hell")
except BatteryQueryError as e:
    # Handle device is unsupported
    print("1")
