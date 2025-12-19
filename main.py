from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
import asyncio
from config import Config
import logging
import traceback
from typing import Callable, Awaitable, Optional
from messages import ServoCommand, AckMessage, TaskFinishedMessage
from camera import Camera
from tracking import calculate_intrinsics, calculate_offset

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
    try:
        async with BleakClient(address) as client:
            logging.info(f"Connected to {address}")
            if callback:
                await callback(client)
    except EOFError:
        logging.warning("Bluetooth connection lost unexpectedly (EOFError)")
    except Exception as e:
        logging.error(f"Connection error: {type(e).__name__}: {str(e)}")
        raise

'''this function will run loop that will send and receive data from the device, until user interupts the program'''
async def test_callback(client: BleakClient, cfg: Config):
    try:
        # left = True
        camera = Camera(cfg.camera_width, cfg.camera_height, cfg.camera_format, show_preview=cfg.camera_debug)
        intrinsics = calculate_intrinsics(cfg)
        
        while True:
            camera.get_frame().get_gray().detect_qr().get_qr_center()
            if camera.current_destination is not None:
                h_offset, v_offset = calculate_offset(intrinsics, camera.current_destination, cfg)
                print(f"Sending command to move to: {h_offset}, {0}")
                message = ServoCommand(h_offset=int(-h_offset), v_offset=int(-v_offset)).to_json().encode()
                await client.write_gatt_char(cfg.uuid, message)
                logging.info(f"Sent: {message.decode()}")
                value = await client.read_gatt_char(cfg.uuid)
                ack = AckMessage.from_json(value.decode())
                logging.info(f"Received: {ack.to_json()}")
                value = await client.read_gatt_char(cfg.uuid)
                task_finished = TaskFinishedMessage.from_json(value.decode())
                logging.info(f"Received Task Finished: {task_finished.to_json()}")
                camera.current_destination = None
            await asyncio.sleep(0.5)
            # if left:
            #     message = ServoCommand(h_offset=-10, v_offset=10).to_json().encode()
            # else:
            #     message = ServoCommand(h_offset=10, v_offset=-10).to_json().encode()
            # left = not left
            # await client.write_gatt_char(cfg.uuid, message)
            # logging.info(f"Sent: {message.decode()}")
            # value = await client.read_gatt_char(cfg.uuid)
            # ack = AckMessage.from_json(value.decode())
            # logging.info(f"Received: {ack.to_json()}")
            # value = await client.read_gatt_char(cfg.uuid)
            # task_finished = TaskFinishedMessage.from_json(value.decode())
            # logging.info(f"Received Task Finished: {task_finished.to_json()}")
            # await asyncio.sleep(0.1)
            
    except (KeyboardInterrupt, asyncio.CancelledError):
        logging.info("User interrupted the program")
        raise
    except Exception as e:
        logging.error(f"Error in test callback: {type(e).__name__}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
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
        logging.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Program terminated gracefully")
    except Exception as e:
        logging.error(f"Fatal error: {type(e).__name__}: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        exit(1)
