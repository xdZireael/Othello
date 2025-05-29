"""
Internals of an othello bitboard, to store the presence or absence of elements on the board
    using single numbers
"""

from __future__ import annotations  # used for self-referencing classes...

from enum import Enum, auto
from copy import copy

import logging


logger = logging.getLogger("Othello")


class Direction(Enum):
    """
    Used to represent a direction we can go to from a case.
    """

    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    NORTH_EAST = auto()
    NORTH_WEST = auto()
    SOUTH_EAST = auto()
    SOUTH_WEST = auto()


class BitboardProperties:
    """Singleton class holding shared bitboard structure properties for each size"""

    _instances = {}

    def __init__(self):
        self.size: int
        self.mask: int
        self.west_mask: int
        self.east_mask: int

    @classmethod
    def get(cls, size: int):
        """Get or create the structure for a given size"""
        if size not in cls._instances:
            structure = cls()
            structure.size = size
            structure.mask = 0
            structure.west_mask = 0
            structure.east_mask = 0
            for i in range(size * size):
                structure.mask |= 1 << i
                structure.west_mask |= (1 << i) if i % size else 0
                structure.east_mask |= (1 << i) if i % size != size - 1 else 0
            cls._instances[size] = structure
        return cls._instances[size]


class Bitboard:
    """Represents a bitboard, a way to represent the presence or absence of
    objects on a board
    """

    def __init__(self, size: int, bits=0):
        """
        Initializes a Bitboard with a given size and bits.
        Uses cached structure properties for the given size.

        :param size: The size of the bitboard.
        :type size: int
        :param bits: The initial state of the bitboard, defaults to 0.
        :type bits: int, optional
        """
        structure = BitboardProperties.get(size)
        self.size = structure.size
        self.mask = structure.mask
        self.west_mask = structure.west_mask
        self.east_mask = structure.east_mask
        self.bits = bits & self.mask

    def __copy__(self):
        result = Bitboard.__new__(Bitboard)
        result.size = self.size
        result.mask = self.mask
        result.west_mask = self.west_mask
        result.east_mask = self.east_mask
        result.bits = self.bits
        return result

    def set(self, x_coord: int, y_coord: int, value: bool) -> None:
        """
        Sets the bit at `x_coord`:`y_coord` to the truth value of `value` (0 if False, else 1).

        :param x_coord: The x coordinate in the board representation.
        :type x_coord: int
        :param y_coord: The y coordinate in the board representation.
        :type y_coord: int
        :param value: The truth value of the bit at `x_coord`:`y_coord`.
        :type value: bool
        """
        bit_idx = self.__coords_to_bit_idx(x_coord, y_coord)
        self.__check_bit_idx_is_legal(bit_idx)
        if value:
            # we simply need to set the corresponding bit to 1 using binary-or
            self.bits |= 1 << bit_idx
        else:
            # a little trickier, we need to generate a mask that has a 0 at the location
            # we want to set to 0, then use a binary with the mask effectively
            # keeping every set bit but the one we are trying to set to 0
            mask = self.mask
            mask ^= 1 << bit_idx
            self.bits &= mask

    def get(self, x_coord: int, y_coord: int) -> bool:
        """
        Get the truth value of a bit `x_coord`:`y_coord` (True if 1, else False).

        :param x_coord: The x coordinate in the board representation.
        :type x_coord: int
        :param y_coord: The y coordinate in the board representation.
        :returns: The value of thus bit
        :rtype: int
        """
        bit_idx = self.__coords_to_bit_idx(x_coord, y_coord)
        self.__check_bit_idx_is_legal(bit_idx)
        mask = 1 << bit_idx
        rez = self.bits & mask
        return rez

    def shift(self, to_dir: Direction):
        """
        Shift a bit in to_direction `dir`.

        :param to_dir: The direction of the shift
        :returns: The result of said shift if it exists
        :rtype: int
        """
        if to_dir == Direction.NORTH:
            shifted = self.__shift_n()
        elif to_dir == Direction.SOUTH:
            shifted = self.__shift_s()
        elif to_dir == Direction.EAST:
            shifted = self.__shift_e()
        elif to_dir == Direction.WEST:
            shifted = self.__shift_w()
        elif to_dir == Direction.NORTH_EAST:
            shifted = self.__shift_ne()
        elif to_dir == Direction.NORTH_WEST:
            shifted = self.__shift_nw()
        elif to_dir == Direction.SOUTH_EAST:
            shifted = self.__shift_se()
        else:
            shifted = self.__shift_sw()
        return shifted

    def popcount(self) -> int:
        """
        popcount (SWAR) simple python port supporting arbitrary-sized bitboards.

        :returns: The number of hot bits in the bitboard representation
        :rtype: int
        """
        summed = 0
        remaining_bits = self.bits
        while remaining_bits > 0:
            chunk_n = remaining_bits & 0xFFFFFFFFFFFFFFFF
            chunk_n = (chunk_n & 0x5555555555555555) + (
                (chunk_n >> 1) & 0x5555555555555555
            )
            chunk_n = (chunk_n & 0x3333333333333333) + (
                (chunk_n >> 2) & 0x3333333333333333
            )
            chunk_n = (chunk_n & 0x0F0F0F0F0F0F0F0F) + (
                (chunk_n >> 4) & 0x0F0F0F0F0F0F0F0F
            )
            chunk_n = (chunk_n & 0x00FF00FF00FF00FF) + (
                (chunk_n >> 8) & 0x00FF00FF00FF00FF
            )
            chunk_n = (chunk_n & 0x0000FFFF0000FFFF) + (
                (chunk_n >> 16) & 0x0000FFFF0000FFFF
            )
            chunk_n = (chunk_n & 0x00000000FFFFFFFF) + (
                (chunk_n >> 32) & 0x00000000FFFFFFFF
            )
            summed += chunk_n
            remaining_bits >>= 64
        return summed

    def hot_bits_coordinates(self) -> list[tuple[int, int]]:
        """
        Returns a list of (x, y) coordinates, one for each hot bit in the bitboard.
        :returns: The list of coordinates set to 1 in the bitboard, in the form list[(x, y)...].
        :rtype: list[tuple[int, int]]
        """
        positions = []
        bits_copy = self.bits
        while bits_copy > 0:
            last_hot_bit = bits_copy & -bits_copy
            position_1d = (last_hot_bit).bit_length() - 1
            positions.append((position_1d % self.size, position_1d // self.size))
            bits_copy &= bits_copy - 1
        return positions

    def empty(self) -> bool:
        """
        Check wether or not the bitboard is empty (popcount of 0).

        :returns: The truth value of the emptyness of the bitboard
        :rtype: bool
        """
        return not self.popcount()

    def __shift_w(self) -> Bitboard:
        """
        Shift all the bits to the west (left).

        :returns: The result of the shift if it exists
        :rtype: int
        """

        clone = copy(self)
        clone.bits = ((self.bits >> 1) & self.east_mask) & self.mask
        return clone

    def __shift_e(self) -> Bitboard:
        """
        Shift all the bits to the east (right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = ((self.bits << 1) & self.west_mask) & self.mask
        return clone

    def __shift_n(self) -> Bitboard:
        """
        Shift all the bits to the north (up).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size) & self.mask
        return clone

    def __shift_s(self) -> Bitboard:
        """
        Shift all the bits to the south (down).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size) & self.mask
        return clone

    def __shift_ne(self) -> Bitboard:
        """
        Shift all the bits to the north-east (up-right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size - 1 & self.west_mask) & self.mask
        return clone

    def __shift_nw(self) -> Bitboard:
        """
        Shift all the bits to the north-west (up-left).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size + 1 & self.east_mask) & self.mask
        return clone

    def __shift_se(self) -> Bitboard:
        """
        Shift all the bits to the south-east (down-right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size + 1 & self.west_mask) & self.mask
        return clone

    def __shift_sw(self) -> Bitboard:
        """
        Shift all the bits to the south-west (down-left).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size - 1 & self.east_mask) & self.mask
        return clone

    def __coords_to_bit_idx(self, x_coord: int, y_coord: int) -> int:
        """
        Convert board coordinates to a bit index.

        This method takes the coordinates of a square on the board, and
        returns the corresponding bit index in the bitboard.

        :param x_coord: The x coordinate of the square.
        :type x_coord: int
        :param y_coord: The y coordinate of the square.
        :type y_coord: int
        :returns: The bit index of the square.
        :rtype: int
        """
        return y_coord * self.size + x_coord

    def __check_bit_idx_is_legal(self, bit_idx: int) -> None:
        """
        Checks if the given bit index is within legal bounds.

        This method ensures that the bit index is within the valid range for the bitboard,
        which is from 0 to size*size - 1. If the index is out of bounds, an IndexError is raised.

        :param bit_idx: The bit index to check.
        :type bit_idx: int

        :raises IndexError: If the bit index is out of legal bounds.
        """

        if not 0 <= bit_idx < (self.size * self.size):
            # avoiding out-of-bound access
            raise IndexError

    def __and__(self, other: Bitboard) -> Bitboard:
        """
        Compute the logical AND of two bitboards.

        This method takes a bitboard `other` and computes the logical AND of the
        current bitboard with `other`. The result is a new bitboard that has a
        1 in each position where both the current bitboard and `other` have a 1.

        :param other: The bitboard to compute the logical AND with.
        :type other: Bitboard
        :return: A bitboard that is the logical AND of the current bitboard and `other`.
        :rtype: Bitboard
        """
        rez = copy(self)
        return Bitboard(self.size, rez.bits & other.bits)

    def __or__(self, other: Bitboard) -> Bitboard:
        """
        Compute the logical OR of two bitboards.

        This method takes a bitboard `other` and computes the logical OR of the
        current bitboard with `other`. The result is a new bitboard that has a
        1 in each position where either the current bitboard or `other` have a 1.

        :param other: The bitboard to compute the logical OR with.
        :type other: Bitboard
        :return: A bitboard that is the logical OR of the current bitboard and `other`.
        :rtype: Bitboard
        """
        rez = copy(self)
        return Bitboard(self.size, rez.bits | other.bits)

    def __xor__(self, other: Bitboard) -> Bitboard:
        """
        Compute the logical XOR of two bitboards.

        This method takes a bitboard `other` and computes the logical XOR of the
        current bitboard with `other`. The result is a new bitboard that has a
        1 in each position where either the current bitboard or `other` have a 1,
        but not both.

        :param other: The bitboard to compute the logical XOR with.
        :type other: Bitboard
        :return: A bitboard that is the logical XOR of the current bitboard and `other`.
        :rtype: Bitboard
        """
        rez = copy(self)
        return Bitboard(self.size, rez.bits ^ other.bits)

    def __invert__(self):
        """
        Compute the binary bitwise invert (~) of two bitboards.

        This method takes a bitboard `other` and computes the logical invert of the
        current bitboard with `other`.

        :param other: The bitboard to compute the binary invert with.
        :type other: Bitboard
        :return: A bitboard that is the binary invert of the current bitboard and `other`.
        :rtype: Bitboard
        """
        rez = copy(self)
        return Bitboard(self.size, ~rez.bits)

    def __eq__(self, other):
        """
        Compare two Bitboard instances for equality.

        This method checks whether the given object `other` is an instance of Bitboard
        and compares its `size` and `bits` attributes with those of the current instance.
        If they are the same, it returns True, indicating the bitboards are equal.
        Otherwise, it returns False.

        :param other: The object to compare with the current Bitboard.
        :type other: Bitboard
        :return: True if the `other` is a Bitboard and both size and bits are equal,
                False otherwise.
        :rtype: bool
        """

        if isinstance(other, Bitboard):
            return other.size == self.size and other.bits == self.bits
        return False

    def __hash__(self):
        """
        Returns a hash value for this bitboard. Two bitboards with the same size
        and the same bits will have the same hash value. This is useful for
        placing bitboards in sets or using them as keys in dictionaries.

        :return: A hash value for this bitboard.
        :rtype int
        """
        return hash((self.size, self.bits))

    def __str__(self) -> str:
        """
        Returns a string representation of the bitboard. Mostly for debugging.

        :return: A string representation of the bitboard showing its x and y dimension.
                "·" for non-empty cases, " " for empty ones.
        :rtype str
        """
        return "\n".join(
            "".join(
                f"{'|' if not x else ''}{'·' if self.get(x, y) else ' '}|"
                for x in range(self.size)
            )
            for y in range(self.size)
        )
