```python
"""
ARINC 429 Adapter Module for CCZ Monitoring System
Version: 1.0.0
Author: CCZ Monitoring Team
Description: ARINC 429 bus communication adapter for real-time CCZ monitoring
"""

import numpy as np
import time
import struct
import threading
import queue
from enum import Enum
from typing import Optional, Dict, List, Tuple, Any
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARINC429Label(Enum):
    """ARINC 429 Standard Labels for Flight Data"""
    # Air Data Computer (ADC) Labels
    ALTITUDE_BAROMETRIC = 0o204  # Barometric altitude
    ALTITUDE_RADIO = 0o205       # Radio altitude
    AIRSPEED_INDICATED = 0o210   # Indicated airspeed
    AIRSPEED_TRUE = 0o211        # True airspeed
    MACH_NUMBER = 0o212          # Mach number
    VERTICAL_SPEED = 0o213       # Vertical speed
    STATIC_AIR_TEMP = 0o214      # Static air temperature
    TOTAL_AIR_TEMP = 0o215       # Total air temperature
    ANGLE_OF_ATTACK = 0o216      # Angle of attack
    PRESSURE_ALTITUDE = 0o217    # Pressure altitude
    
    # Inertial Reference System (IRS) Labels
    PITCH_ANGLE = 0o130          # Pitch angle
    ROLL_ANGLE = 0o131           # Roll angle
    TRUE_HEADING = 0o132         # True heading
    MAGNETIC_HEADING = 0o133     # Magnetic heading
    TRACK_ANGLE = 0o134          # Track angle
    FLIGHT_PATH_ANGLE = 0o135    # Flight path angle
    INERTIAL_ALTITUDE = 0o136    # Inertial altitude
    GROUND_SPEED = 0o137         # Ground speed
    VERTICAL_ACCEL = 0o140       # Vertical acceleration
    LATERAL_ACCEL = 0o141        # Lateral acceleration
    LONGITUDINAL_ACCEL = 0o142   # Longitudinal acceleration
    PITCH_RATE = 0o150           # Pitch rate
    ROLL_RATE = 0o151            # Roll rate
    YAW_RATE = 0o152             # Yaw rate
    
    # Flight Control System (FCS) Labels
    CONTROL_SURFACE_POS = 0o260  # Control surface positions
    FLAP_POSITION = 0o261        # Flap position
    SPOILER_POSITION = 0o262     # Spoiler position
    ELEVATOR_POSITION = 0o263    # Elevator position
    AILERON_POSITION = 0o264     # Aileron position
    RUDDER_POSITION = 0o265      # Rudder position
    
    # Engine Parameters
    ENGINE_N1 = 0o300            # Engine fan speed (%)
    ENGINE_N2 = 0o301            # Engine core speed (%)
    ENGINE_EGT = 0o302           # Exhaust gas temperature
    ENGINE_FUEL_FLOW = 0o303     # Fuel flow
    ENGINE_OIL_PRESS = 0o304     # Oil pressure
    ENGINE_OIL_TEMP = 0o305      # Oil temperature
    ENGINE_VIBRATION = 0o306     # Engine vibration
    
    # Custom Labels for CCZ Monitoring
    CCZ_LYAPUNOV_EXPONENT = 0o500  # λ value
    CCZ_PROBABILITY = 0o501        # CCZ probability
    CCZ_STATUS = 0o502             # CCZ status (0=stable, 1=warning, 2=alert)
    CCZ_CONFIDENCE = 0o503         # Detection confidence
    SYSTEM_HEALTH = 0o504          # System health status

class ARINC429SDI(Enum):
    """Source/Destination Identifier"""
    ADC = 0b00      # Air Data Computer
    IRS = 0b01      # Inertial Reference System
    FMS = 0b10      # Flight Management System
    CCZ_MONITOR = 0b11  # CCZ Monitoring System

class ARINC429Parity(Enum):
    """Parity Options"""
    ODD = 0
    EVEN = 1

@dataclass
class ARINC429Message:
    """ARINC 429 Message Structure"""
    label: int                    # 8-bit label (octal format)
    sdi: int = 0                  # 2-bit Source/Destination Identifier
    data: int = 0                 # 19-bit data field
    ssm: int = 0                  # 2-bit Sign/Status Matrix
    parity: int = 0               # 1-bit parity
    
    def to_word(self) -> int:
        """Convert message to 32-bit ARINC 429 word"""
        word = (
            (self.label & 0xFF) |          # Bits 1-8: Label
            ((self.sdi & 0x03) << 8) |     # Bits 9-10: SDI
            ((self.data & 0x7FFFF) << 10) | # Bits 11-29: Data
            ((self.ssm & 0x03) << 29) |    # Bits 30-31: SSM
            ((self.parity & 0x01) << 31)    # Bit 32: Parity
        )
        return word & 0xFFFFFFFF
    
    @classmethod
    def from_word(cls, word: int) -> 'ARINC429Message':
        """Create message from 32-bit ARINC 429 word"""
        label = word & 0xFF
        sdi = (word >> 8) & 0x03
        data = (word >> 10) & 0x7FFFF
        ssm = (word >> 29) & 0x03
        parity = (word >> 31) & 0x01
        return cls(label, sdi, data, ssm, parity)
    
    def calculate_parity(self) -> int:
        """Calculate odd parity for the word"""
        word = self.to_word() & 0x7FFFFFFF  # Mask out parity bit
        parity = bin(word).count('1') % 2
        return parity ^ 1  # Return odd parity
    
    def validate_parity(self) -> bool:
        """Validate parity of the message"""
        return self.parity == self.calculate_parity()
    
    def __str__(self) -> str:
        return (f"ARINC429Message(label={oct(self.label)}, "
                f"SDI={self.sdi:02b}, data={self.data:05X}, "
                f"SSM={self.ssm:02b}, parity={self.parity})")

class ARINC429DataEncoder:
    """Encoder for various data types to ARINC 429 format"""
    
    @staticmethod
    def encode_bnr(value: float, bits: int = 19, scale: float = 1.0, 
                   offset: float = 0.0, signed: bool = False) -> int:
        """
        Encode Binary Number Representation (BNR)
        
        Args:
            value: Value to encode
            bits: Number of bits for data field (max 19)
            scale: Scaling factor
            offset: Offset value
            signed: Whether value is signed
            
        Returns:
            Encoded integer
        """
        # Apply scale and offset
        scaled_value = (value - offset) / scale
        
        # Handle signed values
        if signed:
            max_val = (1 << (bits - 1)) - 1
            min_val = -(1 << (bits - 1))
            scaled_value = max(min(scaled_value, max_val), min_val)
            
            # Convert to two's complement if negative
            if scaled_value < 0:
                scaled_value = (1 << bits) + scaled_value
        else:
            max_val = (1 << bits) - 1
            scaled_value = max(min(scaled_value, max_val), 0)
        
        return int(scaled_value) & ((1 << bits) - 1)
    
    @staticmethod
    def decode_bnr(data: int, bits: int = 19, scale: float = 1.0,
                   offset: float = 0.0, signed: bool = False) -> float:
        """
        Decode Binary Number Representation (BNR)
        """
        if signed:
            # Check if value is negative (MSB set)
            if data & (1 << (bits - 1)):
                # Two's complement conversion
                data = data - (1 << bits)
        
        value = data * scale + offset
        return value
    
    @staticmethod
    def encode_bcd(value: float, decimal_places: int = 0) -> int:
        """
        Encode Binary Coded Decimal (BCD)
        """
        # Scale value based on decimal places
        scaled_value = int(value * (10 ** decimal_places))
        
        # Convert to BCD
        bcd_value = 0
        shift = 0
        while scaled_value > 0:
            bcd_value |= (scaled_value % 10) << shift
            scaled_value //= 10
            shift += 4
        
        return bcd_value & 0x7FFFF  # 19-bit limit
    
    @staticmethod
    def decode_bcd(data: int, decimal_places: int = 0) -> float:
        """
        Decode Binary Coded Decimal (BCD)
        """
        value = 0
        multiplier = 1
        
        while data > 0:
            digit = data & 0xF
            value += digit * multiplier
            data >>= 4
            multiplier *= 10
        
        return value / (10 ** decimal_places)
    
    @staticmethod
    def encode_discrete(states: List[bool]) -> int:
        """
        Encode discrete states into data field
        """
        data = 0
        for i, state in enumerate(states):
            if i >= 19:  # 19-bit limit
                break
            if state:
                data |= (1 << i)
        return data

class CCZDataAdapter:
    """Adapter for CCZ data to ARINC 429 format"""
    
    # CCZ parameter encoding schemes
    ENCODING_SCHEMES = {
        ARINC429Label.CCZ_LYAPUNOV_EXPONENT: {
            'type': 'BNR',
            'bits': 16,
            'scale': 0.0001,
            'offset': -1.0,
            'signed': True,
            'range': (-1.0, 2.0)
        },
        ARINC429Label.CCZ_PROBABILITY: {
            'type': 'BNR',
            'bits': 16,
            'scale': 0.00001526,  # 1/65535
            'offset': 0.0,
            'signed': False,
            'range': (0.0, 1.0)
        },
        ARINC429Label.CCZ_STATUS: {
            'type': 'BNR',
            'bits': 3,
            'scale': 1.0,
            'offset': 0.0,
            'signed': False,
            'range': (0, 7)
        },
        ARINC429Label.CCZ_CONFIDENCE: {
            'type': 'BNR',
            'bits': 8,
            'scale': 0.00392157,  # 1/255
            'offset': 0.0,
            'signed': False,
            'range': (0.0, 1.0)
        },
        ARINC429Label.SYSTEM_HEALTH: {
            'type': 'Discrete',
            'bits': 8,
            'states': ['power_ok', 'sensor_ok', 'processor_ok', 
                      'memory_ok', 'comms_ok', 'calibration_ok',
                      'temp_ok', 'voltage_ok']
        }
    }
    
    @classmethod
    def encode_ccz_data(cls, label: ARINC429Label, value: Any) -> Optional[ARINC429Message]:
        """
        Encode CCZ data to ARINC 429 message
        """
        if label not in cls.ENCODING_SCHEMES:
            logger.error(f"Unsupported label for encoding: {label}")
            return None
        
        scheme = cls.ENCODING_SCHEMES[label]
        
        if scheme['type'] == 'BNR':
            # Validate range
            if 'range' in scheme:
                min_val, max_val = scheme['range']
                if isinstance(value, (int, float)):
                    value = max(min(value, max_val), min_val)
            
            # Encode BNR
            data = ARINC429DataEncoder.encode_bnr(
                value,
                bits=scheme['bits'],
                scale=scheme['scale'],
                offset=scheme.get('offset', 0.0),
                signed=scheme.get('signed', False)
            )
        elif scheme['type'] == 'BCD':
            decimal_places = scheme.get('decimal_places', 0)
            data = ARINC429DataEncoder.encode_bcd(value, decimal_places)
        elif scheme['type'] == 'Discrete':
            if isinstance(value, list):
                data = ARINC429DataEncoder.encode_discrete(value)
            else:
                logger.error("Discrete encoding requires list of boolean states")
                return None
        else:
            logger.error(f"Unknown encoding type: {scheme['type']}")
            return None
        
        # Create message
        message = ARINC429Message(
            label=label.value,
            sdi=ARINC429SDI.CCZ_MONITOR.value,
            data=data,
            ssm=0b01,  # Normal operation
            parity=0
        )
        
        # Calculate and set parity
        message.parity = message.calculate_parity()
        
        return message
    
    @classmethod
    def decode_ccz_data(cls, message: ARINC429Message) -> Optional[Dict[str, Any]]:
        """
        Decode ARINC 429 message to CCZ data
        """
        label = ARINC429Label(message.label)
        
        if label not in cls.ENCODING_SCHEMES:
            logger.error(f"Unsupported label for decoding: {label}")
            return None
        
        scheme = cls.ENCODING_SCHEMES[label]
        
        if scheme['type'] == 'BNR':
            value = ARINC429DataEncoder.decode_bnr(
                message.data,
                bits=scheme['bits'],
                scale=scheme['scale'],
                offset=scheme.get('offset', 0.0),
                signed=scheme.get('signed', False)
            )
        elif scheme['type'] == 'BCD':
            decimal_places = scheme.get('decimal_places', 0)
            value = ARINC429DataEncoder.decode_bcd(message.data, decimal_places)
        elif scheme['type'] == 'Discrete':
            # For discrete, return the raw bits
            value = message.data
        else:
            logger.error(f"Unknown encoding type: {scheme['type']}")
            return None
        
        return {
            'label': label,
            'value': value,
            'sdi': message.sdi,
            'ssm': message.ssm,
            'timestamp': datetime.now(),
            'valid_parity': message.validate_parity()
        }

class ARINC429BusEmulator:
    """Emulator for ARINC 429 bus communication"""
    
    def __init__(self, bus_speed: int = 100000,  # 100 kbps
                 tx_channels: int = 4,
                 rx_channels: int = 4):
        self.bus_speed = bus_speed
        self.tx_channels = tx_channels
        self.rx_channels = rx_channels
        self.tx_queues = [queue.Queue() for _ in range(tx_channels)]
        self.rx_queues = [queue.Queue() for _ in range(rx_channels)]
        self.running = False
        self.threads = []
        self.callbacks = {}
        
        # Statistics
        self.stats = {
            'tx_messages': 0,
            'rx_messages': 0,
            'parity_errors': 0,
            'format_errors': 0,
            'tx_bytes': 0,
            'rx_bytes': 0
        }
    
    def start(self):
        """Start bus emulator"""
        if self.running:
            logger.warning("Bus emulator already running")
            return
        
        self.running = True
        
        # Start transmission threads
        for channel in range(self.tx_channels):
            thread = threading.Thread(
                target=self._tx_thread,
                args=(channel,),
                name=f"ARINC429-TX-{channel}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        # Start reception threads
        for channel in range(self.rx_channels):
            thread = threading.Thread(
                target=self._rx_thread,
                args=(channel,),
                name=f"ARINC429-RX-{channel}",
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
        
        logger.info(f"ARINC 429 Bus Emulator started at {self.bus_speed} bps")
    
    def stop(self):
        """Stop bus emulator"""
        self.running = False
        for thread in self.threads:
            thread.join(timeout=1.0)
        self.threads.clear()
        logger.info("ARINC 429 Bus Emulator stopped")
    
    def transmit(self, channel: int, message: ARINC429Message) -> bool:
        """
        Transmit message on specified channel
        """
        if channel >= self.tx_channels:
            logger.error(f"Invalid TX channel: {channel}")
            return False
        
        try:
            self.tx_queues[channel].put(message, timeout=0.1)
            self.stats['tx_messages'] += 1
            self.stats['tx_bytes'] += 4  # 32 bits = 4 bytes
            return True
        except queue.Full:
            logger.warning(f"TX queue full on channel {channel}")
            return False
    
    def register_callback(self, label: ARINC429Label, 
                         callback: callable, channel: int = 0):
        """
        Register callback for specific label
        """
        if label not in self.callbacks:
            self.callbacks[label] = []
        
        self.callbacks[label].append({
            'channel': channel,
            'callback': callback
        })
    
    def _tx_thread(self, channel: int):
        """Transmission thread"""
        bit_time = 1.0 / self.bus_speed
        
        while self.running:
            try:
                message = self.tx_queues[channel].get(timeout=0.1)
                
                # Simulate transmission delay
                time.sleep(bit_time * 32)  # 32 bits per word
                
                # Broadcast to all RX channels
                for rx_channel in range(self.rx_channels):
                    if not self.rx_queues[rx_channel].full():
                        self.rx_queues[rx_channel].put(message)
                
                logger.debug(f"TX Channel {channel}: {message}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"TX thread error on channel {channel}: {e}")
    
    def _rx_thread(self, channel: int):
        """Reception thread"""
        while self.running:
            try:
                message = self.rx_queues[channel].get(timeout=0.1)
                
                # Update statistics
                self.stats['rx_messages'] += 1
                self.stats['rx_bytes'] += 4
                
                # Check parity
                if not message.validate_parity():
                    self.stats['parity_errors'] += 1
                    logger.warning(f"Parity error on channel {channel}")
                    continue
                
                # Decode message
                label = ARINC429Label(message.label)
                
                # Call registered callbacks
                if label in self.callbacks:
                    for handler in self.callbacks[label]:
                        if handler['channel'] == channel:
                            try:
                                handler['callback'](message)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                
                logger.debug(f"RX Channel {channel}: {message}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"RX thread error on channel {channel}: {e}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get bus statistics"""
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics"""
        self.stats = {
            'tx_messages': 0,
            'rx_messages': 0,
            'parity_errors': 0,
            'format_errors': 0,
            'tx_bytes': 0,
            'rx_bytes': 0
        }

class CCZARINC429Interface:
    """Main interface for CCZ monitoring system to ARINC 429"""
    
    def __init__(self, bus_channel: int = 0):
        self.bus_channel = bus_channel
        self.bus = ARINC429BusEmulator()
        self.data_adapter = CCZDataAdapter()
        self.ccz_state = {
            'lyapunov_exponent': 0.0,
            'probability': 0.0,
            'status': 0,
            'confidence': 0.0,
            'health': [True] * 8
        }
        self.running = False
        self.update_interval = 0.1  # 10 Hz update rate
        self.thread = None
        
        # Register callbacks for flight data
        self._register_callbacks()
    
    def _register_callbacks(self):
        """Register callbacks for received flight data"""
        flight_data_labels = [
            ARINC429Label.PITCH_ANGLE,
            ARINC429Label.ROLL_ANGLE,
            ARINC429Label.VERTICAL_ACCEL,
            ARINC429Label.ALTITUDE_BAROMETRIC,
            ARINC429Label.AIRSPEED_INDICATED
        ]
        
        for label in flight_data_labels:
            self.bus.register_callback(label, self._handle_flight_data)
    
    def _handle_flight_data(self, message: ARINC429Message):
        """Handle incoming flight data"""
        decoded = self.data_adapter.decode_ccz_data(message)
        if decoded:
            logger.info(f"Received flight data: {decoded}")
            # Here you would integrate this data into CCZ calculations
    
    def start(self):
        """Start ARINC 429 interface"""
        if self.running:
            logger.warning("Interface already running")
            return
        
        self.bus.start()
        self.running = True
        
        # Start data publishing thread
        self.thread = threading.Thread(
            target=self._publish_ccz_data,
            name="CCZ-ARINC429-Publisher",
            daemon=True
        )
        self.thread.start()
        
        logger.info("CCZ ARINC 429 Interface started")
    
    def stop(self):
        """Stop ARINC 429 interface"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        self.bus.stop()
        logger.info("CCZ ARINC 429 Interface stopped")
    
    def update_ccz_state(self, lyapunov: float, probability: float, 
                        status: int, confidence: float, health: List[bool]):
        """Update CCZ state for transmission"""
        self.ccz_state.update({
            'lyapunov_exponent': lyapunov,
            'probability': probability,
            'status': status,
            'confidence': confidence,
            'health': health
        })
    
    def _publish_ccz_data(self):
        """Publish CCZ data on ARINC 429 bus"""
        while self.running:
            try:
                # Encode and transmit CCZ Lyapunov exponent
                lambda_msg = self.data_adapter.encode_ccz_data(
                    ARINC429Label.CCZ_LYAPUNOV_EXPONENT,
                    self.ccz_state['lyapunov_exponent']
                )
                if lambda_msg:
                    self.bus.transmit(self.bus_channel, lambda_msg)
                
                # Encode and transmit CCZ probability
                prob_msg = self.data_adapter.encode_ccz_data(
                    ARINC429Label.CCZ_PROBABILITY,
                    self.ccz_state['probability']
                )
                if prob_msg:
                    self.bus.transmit(self.bus_channel, prob_msg)
                
                # Encode and transmit CCZ status
                status_msg = self.data_adapter.encode_ccz_data(
                    ARINC429Label.CCZ_STATUS,
                    self.ccz_state['status']
                )
                if status_msg:
                    self.bus.transmit(self.bus_channel, status_msg)
                
                # Encode and transmit confidence
                conf_msg = self.data_adapter.encode_ccz_data(
                    ARINC429Label.CCZ_CONFIDENCE,
                    self.ccz_state['confidence']
                )
                if conf_msg:
                    self.bus.transmit(self.bus_channel, conf_msg)
                
                # Encode and transmit system health
                health_msg = self.data_adapter.encode_ccz_data(
                    ARINC429Label.SYSTEM_HEALTH,
                    self.ccz_state['health']
                )
                if health_msg:
                    self.bus.transmit(self.bus_channel, health_msg)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error publishing CCZ data: {e}")
                time.sleep(1.0)
    
    def get_bus_statistics(self) -> Dict[str, Any]:
        """Get interface statistics"""
        stats = self.bus.get_statistics()
        stats.update({
            'update_interval': self.update_interval,
            'bus_channel': self.bus_channel,
            'running': self.running
        })
        return stats
    
    def send_custom_message(self, label: int, data: Any) -> bool:
        """Send custom ARINC 429 message"""
        # Create custom message
        message = ARINC429Message(
            label=label,
            sdi=ARINC429SDI.CCZ_MONITOR.value,
            data=data,
            ssm=0b01,
            parity=0
        )
        message.parity = message.calculate_parity()
        
        return self.bus.transmit(self.bus_channel, message)

# Example usage
def example_usage():
    """Example of using the ARINC 429 adapter"""
    
    # Create interface
    interface = CCZARINC429Interface(bus_channel=0)
    
    try:
        # Start interface
        interface.start()
        
        # Simulate CCZ data updates
        for i in range(10):
            # Generate synthetic CCZ data
            lyapunov = np.random.uniform(-0.1, 0.3)
            probability = np.random.uniform(0.0, 1.0)
            status = 0 if probability < 0.3 else 1 if probability < 0.7 else 2
            confidence = np.random.uniform(0.8, 1.0)
            health = [True] * 8
            
            # Update interface
            interface.update_ccz_state(lyapunov, probability, status, confidence, health)
            
            # Get statistics
            stats = interface.get_bus_statistics()
            print(f"Iteration {i+1}:")
            print(f"  Lyapunov: {lyapunov:.4f}")
            print(f"  Probability: {probability:.3f}")
            print(f"  Status: {status}")
            print(f"  TX Messages: {stats['tx_messages']}")
            print(f"  RX Messages: {stats['rx_messages']}")
            print()
            
            time.sleep(1.0)
        
        # Display final statistics
        final_stats = interface.get_bus_statistics()
        print("\nFinal Statistics:")
        for key, value in final_stats.items():
            print(f"  {key}: {value}")
    
    finally:
        # Stop interface
        interface.stop()

if __name__ == "__main__":
    example_usage()
```

This ARINC 429 adapter provides:

Key Features:

1. Complete ARINC 429 Implementation:
   · 32-bit word structure (Label + SDI + Data + SSM + Parity)
   · BNR (Binary Number Representation) encoding/decoding
   · BCD (Binary Coded Decimal) encoding/decoding
   · Discrete state encoding
   · Odd parity calculation and validation
2. CCZ-Specific Integration:
   · Custom ARINC 429 labels for CCZ monitoring (500-504 octal)
   · Specialized encoding schemes for Lyapunov exponents and probabilities
   · Health monitoring and status reporting
3. Bus Emulation:
   · Multi-channel TX/RX emulation
   · Configurable bus speed (standard 100 kbps)
   · Thread-safe queue-based communication
   · Callback system for message handling
4. Statistics & Monitoring:
   · Message counters
   · Error tracking (parity errors, format errors)
   · Bandwidth monitoring
   · Health status reporting

Usage Example:

```python
# Quick start
interface = CCZARINC429Interface()
interface.start()

# Update CCZ data
interface.update_ccz_state(
    lyapunov=0.152,
    probability=0.87,
    status=2,  # Alert
    confidence=0.95,
    health=[True, True, True, True, True, True, True, True]
)

# Get statistics
stats = interface.get_bus_statistics()
```

The adapter is designed for both simulation/testing and potential integration with actual ARINC 429 hardware interfaces.