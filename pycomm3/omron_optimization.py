"""
Omron FINS Optimization Module

This module provides the OmronOptimizer class, which implements smart batch reading strategies
to minimize network round-trips when communicating with Omron PLCs.
"""

import struct
from typing import List, Union, Dict, Any, Optional
from pyomron_fins.fins_client import FinsClient, FinsAddress

class OmronOptimizer:
    """
    Optimizes Omron FINS communication by grouping read requests.
    """
    
    def __init__(self, client: FinsClient):
        """
        Initialize with an existing connected FinsClient.
        
        Args:
            client: Connected FinsClient instance
        """
        self.client = client

    def read_smart(self, addresses: List[Union[str, FinsAddress]]) -> Dict[str, Any]:
        """
        Intelligently reads a list of addresses using the most efficient strategy.
        
        Strategies:
        1. If addresses are contiguous (or close), use Memory Area Read (0x0101).
        2. If addresses are scattered, use Multiple Memory Area Read (0x0104).
        3. If too many scattered addresses, split into multiple 0x0104 batches.
        
        Args:
            addresses: List of address strings (e.g., 'D100', 'D101') or FinsAddress objects.
            
        Returns:
            Dictionary mapping address string to value.
        """
        if not addresses:
            return {}

        # 1. Normalize addresses to FinsAddress objects
        fins_addresses = []
        for addr in addresses:
            if isinstance(addr, str):
                fins_addresses.append(FinsAddress.from_string(addr))
            else:
                fins_addresses.append(addr)

        # 2. Sort addresses to check for contiguity
        # Group by memory area first
        grouped_by_area = {}
        for fa in fins_addresses:
            if fa.area not in grouped_by_area:
                grouped_by_area[fa.area] = []
            grouped_by_area[fa.area].append(fa)

        results = {}

        for area, area_addresses in grouped_by_area.items():
            # Sort by address index
            area_addresses.sort(key=lambda x: x.address)
            
            # Simple strategy: Check if they are mostly contiguous
            # If the range (max - min) is close to the count, it's efficient to read the block
            min_addr = area_addresses[0].address
            max_addr = area_addresses[-1].address
            count = len(area_addresses)
            span = max_addr - min_addr + 1
            
            # Heuristic: If reading the whole block reads less than 2x the needed data, do it.
            # Also consider FINS limit (approx 999 words per read)
            if span <= 990 and span < (count * 2):
                # Strategy: Read Contiguous Block
                block_values = self.read_contiguous_block(area, min_addr, span)
                if block_values:
                    # Map back to requested addresses
                    for fa in area_addresses:
                        offset = fa.address - min_addr
                        if 0 <= offset < len(block_values):
                            results[str(fa)] = block_values[offset]
            else:
                # Strategy: Read Multiple (Scattered)
                # FINS 0x0104 allows max ~32 addresses per command (safe limit)
                batch_size = 30
                for i in range(0, len(area_addresses), batch_size):
                    batch = area_addresses[i:i+batch_size]
                    batch_results = self.client.read_multiple(batch)
                    results.update(batch_results)

        return results

    def read_contiguous_block(self, area: str, start_address: int, count: int) -> List[int]:
        """
        Reads a contiguous block of words.
        
        Args:
            area: Memory area (e.g., 'DM')
            start_address: Starting word address
            count: Number of words to read
            
        Returns:
            List of integer values
        """
        try:
            # Construct address string manually or use FinsAddress
            # Using FinsAddress to be consistent
            start_node = FinsAddress(area, start_address)
            return self.client.read(start_node, count)
        except Exception as e:
            print(f"Error reading block {area}{start_address} len {count}: {e}")
            return []

    def read_real_batch(self, addresses: List[Union[str, FinsAddress]]) -> Dict[str, float]:
        """
        Reads multiple REAL (float) values.
        
        Since REALs take 2 words, this requires reading 2x words and parsing.
        
        Args:
            addresses: List of starting addresses for REALs (e.g. D100 means D100+D101)
            
        Returns:
            Dictionary mapping address to float value
        """
        # For REALs, we need to read 2 words per address.
        # We can reuse read_smart but we need to handle the word pairing.
        
        # 1. Identify all words needed (addr and addr+1)
        word_addresses = []
        map_real_to_words = {} # "D100" -> ["D100", "D101"]
        
        for addr in addresses:
            if isinstance(addr, str):
                fa = FinsAddress.from_string(addr)
            else:
                fa = addr
                
            w1 = fa
            w2 = FinsAddress(fa.area, fa.address + 1)
            
            word_addresses.append(w1)
            word_addresses.append(w2)
            
            map_real_to_words[str(fa)] = (str(w1), str(w2))
            
        # 2. Read all words using smart reader
        raw_values = self.read_smart(word_addresses)
        
        # 3. Reconstruct floats
        results = {}
        for real_addr_str, (w1_str, w2_str) in map_real_to_words.items():
            if w1_str in raw_values and w2_str in raw_values:
                val1 = raw_values[w1_str]
                val2 = raw_values[w2_str]
                
                # Pack into bytes and unpack as float
                # OMRON Float: Word Swapped Big Endian
                # Words are [High Word] [Low Word] in memory order?
                # Based on previous code:
                # float_bytes = response[:4] (which is w1_bytes + w2_bytes)
                # swapped = float_bytes[2:4] + float_bytes[0:2]
                # So w2 is high part, w1 is low part?
                
                # Let's verify with previous code logic:
                # response = [byte1, byte2, byte3, byte4]
                # w1 = (byte1<<8) | byte2
                # w2 = (byte3<<8) | byte4
                # float_bytes = byte1, byte2, byte3, byte4
                # swapped = byte3, byte4, byte1, byte2
                
                # So we need:
                bytes_w1 = struct.pack('>H', val1)
                bytes_w2 = struct.pack('>H', val2)
                
                swapped_bytes = bytes_w2 + bytes_w1
                try:
                    float_val = struct.unpack('>f', swapped_bytes)[0]
                    results[real_addr_str] = float_val
                except:
                    results[real_addr_str] = None
                    
        return results
