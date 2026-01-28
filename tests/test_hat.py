import unittest
import time

import asyncio

from ..examples.common import create_mesh_node, print_packet_info

from pymc_core.protocol import Packet
from pymc_core.protocol.packet_builder import PacketBuilder

try:
    import RPi.GPIO as GPIO # type: ignore
except ImportError:
    GPIO = None  # Allow tests to be imported on non-Pi systems

def get_user_confirmation(prompt: str) -> bool:
        """Ask user for y/n confirmation."""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            print("Please enter 'y' or 'n'")


class TestMessageSend(unittest.TestCase):

    async def send_text_message(self, radio_type: str = "hat_radio1"):
        """Send a text message with CRC validation."""
        print("Starting text message send example...")

        mesh_node, identity = create_mesh_node("MessageSender", radio_type)
        packet = Packet()

        class MockContact:
            def __init__(self, name, pubkey_hex):
                self.name = name
                self.public_key = pubkey_hex
                self.out_path = []

        mock_contact = MockContact(
            "TestRecipient",
            "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        )

        message_text = "Testing new Dual SX1252 HAT by VoltaraLabs!"
        print(f"Message: {message_text}")
        print("Creating text message packet...")

        success = False
        try:
            packet, crc = PacketBuilder.create_text_message(
                contact=mock_contact,
                local_identity=identity,
                message=message_text,
                attempt=0,
                message_type="flood",
            )

            print_packet_info(packet, "Created text message packet")
            print(f"CRC: {crc:08X}")
            print("Sending message...")

            success = await mesh_node.dispatcher.send_packet(packet, wait_for_ack=True)

            if success:
                print("Message sent successfully with ACK received!")
                print(f"Delivered: {message_text}")
            else:
                print("Failed to send message - no ACK received")

        except Exception as e:
            print(f"Error: {e}")

        return success

    def test_message_send_radio1(self):
        self.assertTrue(asyncio.run(self.send_text_message("hat_radio1")), "Should be true")

    def test_message_send_radio2(self):
        self.assertTrue(asyncio.run(self.send_text_message("hat_radio2")), "Should be true")



class TestLeds(unittest.TestCase):

    # LED pin configurations
    RADIO1_RX_LED = 17
    RADIO1_TX_LED = 27
    RADIO2_RX_LED = 5
    RADIO2_TX_LED = 16

    def _blink_leds(self, rx_pin: int, tx_pin: int, interval_ms: int = 500, duration_s: int = 3):
        """Blink two LEDs alternately."""
        GPIO.setup(rx_pin, GPIO.OUT)
        GPIO.setup(tx_pin, GPIO.OUT)

        interval_s = interval_ms / 1000
        cycles = int(duration_s / interval_s)

        for i in range(cycles):
            GPIO.output(rx_pin, i % 2 == 0)
            GPIO.output(tx_pin, i % 2 == 1)
            time.sleep(interval_s)

        GPIO.output(rx_pin, False)
        GPIO.output(tx_pin, False)

    def test_leds_visual_radio1(self):
        """Test radio1 LEDs with visual confirmation."""
        print(f"\nBlinking Radio 1 LEDs (RX=GPIO{self.RADIO1_RX_LED}, TX=GPIO{self.RADIO1_TX_LED})...")
        self._blink_leds(self.RADIO1_RX_LED, self.RADIO1_TX_LED)

        result = self._get_user_confirmation("Did the Radio 1 LEDs blink alternately?")
        self.assertTrue(result, "User reported LEDs did not blink correctly")

    def test_leds_visual_radio2(self):
        """Test radio2 LEDs with visual confirmation."""
        print(f"\nBlinking Radio 2 LEDs (RX=GPIO{self.RADIO2_RX_LED}, TX=GPIO{self.RADIO2_TX_LED})...")
        self._blink_leds(self.RADIO2_RX_LED, self.RADIO2_TX_LED)

        result = self._get_user_confirmation("Did the Radio 2 LEDs blink alternately?")
        self.assertTrue(result, "User reported LEDs did not blink correctly")

if __name__ == "__main__":
    unittest.main()