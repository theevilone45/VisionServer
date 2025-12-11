from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
import asyncio
from config import Config
import logging
from typing import Callable, Awaitable, Optional
from messages import ServoCommand, AckMessage

def init_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def list_devices() -> list[BLEDevice]:
    devices = await BleakScanner.discover()
    logging.info(f"Discovered devices: {devices}")
    return devices

def match_device(devices: list[BLEDevice], target_name: str) -> str | None:
    for d in devices:
        if d.name and target_name in d.name:
            logging.info(f"Matched device: {d}")
            return d.address
    logging.warning(f"No device matched with name: {target_name}")
    return None

async def run(address: str, callback: Optional[Callable[[BleakClient], Awaitable[None]]] = None):
    async with BleakClient(address) as client:
        logging.info(f"Connected to {address}")
        if callback:
            await callback(client)

'''this function will run loop that will send and receive data from the device, until user interupts the program'''
async def test_callback(client: BleakClient, cfg: Config):
    try:
        # counter : int = 0
        while True:
            message = ServoCommand(servo1_offset=10, servo2_offset=20).to_json().encode()
            await client.write_gatt_char(cfg.uuid, message)
            logging.info(f"Sent: {message.decode()}")
        
            value = await client.read_gatt_char(cfg.uuid)
            ack = AckMessage.from_json(value.decode())
            logging.info(f"Received: {ack.to_json()}")
            
            await asyncio.sleep(0.05)
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("User interrupted the program")
        raise
    except Exception as e:
        logging.error(f"Error in test callback: {e}")
        raise



async def main():
    init_logging()
    config = Config.from_args()
    logging.info(f"Using configuration: {config}")
    
    try:
        devices = await list_devices()
        address = match_device(devices, config.device_name)
        if address:
            await run(address, lambda client: test_callback(client, config))
        else:
            logging.error("No matching device found. Exiting.")
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("Program interrupted gracefully")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated gracefully")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)
