"""
Testing the agnostic bitboard implementation
"""

import pytest
import random

from othello.bitboard import Bitboard, Direction


def test_init_2():
    """
    Tests the initialization of a Bitboard with a size of 2.

    The west and east masks should be 1010 and 0101 respectively.
    """
    b_2 = Bitboard(2)

    assert b_2.mask == 0b1111
    assert b_2.west_mask == 0b1010
    assert b_2.east_mask == 0b0101


def test_init_8():
    """
    Tests the initialization of a Bitboard with a size of 8.

    The mask should be a binary string of 8 * 8 = 64 ones.
    The west mask should be a binary string of 8 * 8 = 64 ones,
        with the first and last bits of every row set to 0.
    The east mask should be a binary string of 8 * 8 = 64 ones,
        with the first and last bits of every row set to 0, shifted one bit to the left.
    """
    b_8 = Bitboard(8)

    assert (
        b_8.mask == 0b1111111111111111111111111111111111111111111111111111111111111111
    )
    assert (
        b_8.west_mask
        == 0b1111111011111110111111101111111011111110111111101111111011111110
    )
    assert (
        b_8.east_mask
        == 0b0111111101111111011111110111111101111111011111110111111101111111
    )


def test_oob_access():
    """
    Tests the out-of-bounds access of a Bitboard.

    The bit at 0, 6 should raise an IndexError.
    """
    b = Bitboard(6)

    with pytest.raises(IndexError):
        b.set(0, 6, True)


def test_set():
    """
    Test the set method of the Bitboard class.

    This test checks if the set method correctly sets and unsets bits at specified coordinates.
    It initializes a 4x4 Bitboard, sets bits at (0, 0), (3, 3), and (1, 1) to True, and verifies the bits field.
    Then, it unsets the bit at (3, 3) and verifies the updated bits field.
    """

    b = Bitboard(4)
    b.set(0, 0, True)
    b.set(3, 3, True)
    b.set(1, 1, True)

    assert b.bits == 0b1000000000100001
    b.set(3, 3, False)

    assert b.bits == 0b0000000000100001


def test_get():
    """
    Test the get method of the Bitboard class.

    This test checks if the get method accurately retrieves the truth value of bits
    at specified coordinates. It initializes a 6x6 Bitboard, sets bits at (0, 3) and
    (4, 5) to True, and verifies that the get method returns True for these coordinates
    and False for unset coordinates such as (4, 2) and (0, 0).
    """

    b = Bitboard(6)
    b.set(0, 3, True)
    b.set(4, 5, True)

    assert b.get(0, 3) and b.get(4, 5) and not b.get(4, 2) and not b.get(0, 0)


"""
| | | |·| |
|·| | | | |
| | | | |·|
| | |·| | |
|·| | | | |
"""
pytest.b = Bitboard(5)
pytest.b.bits = 0b0000100100100000000101000


def test_shift_n():
    """
    |·| | | | |
    | | | | |·|
    | | |·| | |
    |·| | | | |
    | | | | | |
    """

    shifted_b = pytest.b.shift(Direction.NORTH)

    assert shifted_b.bits == 0b0000000001001001000000001


def test_shift_s():
    """
    | | | | | |
    | | | |·| |
    |·| | | | |
    | | | | |·|
    | | |·| | |
    """

    shifted_b = pytest.b.shift(Direction.SOUTH)

    assert (shifted_b.bits & shifted_b.mask) == (
        0b0010010000000010100000000 & shifted_b.mask
    )


def test_shift_w():
    """
    | | |·| | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    """

    shifted_b = pytest.b.shift(Direction.WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000010010000000000100 & shifted_b.mask
    )


def test_e():
    """
    | | | | |·|
    | |·| | | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    """

    shifted_b = pytest.b.shift(Direction.EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0001001000000000001010000 & shifted_b.mask
    )


def test_ne():
    """
    | |·| | | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    """

    shifted_b = pytest.b.shift(Direction.NORTH_EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000010010000000000010 & shifted_b.mask
    )


def test_nw():
    """
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    | | | | | |
    """

    shifted_b = pytest.b.shift(Direction.NORTH_WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000000000100100000000 & shifted_b.mask
    )


def test_se():
    """
    | | | | | |
    | | | | |·|
    | |·| | | |
    | | | | | |
    | | | |·| |
    """

    shifted_b = pytest.b.shift(Direction.SOUTH_EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0100000000000101000000000 & shifted_b.mask
    )


def test_sw():
    """
    | | | | | |
    | | |·| | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    """

    shifted_b = pytest.b.shift(Direction.SOUTH_WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0001001000000000010000000 & shifted_b.mask
    )


def test_popcount_16_5():
    b = Bitboard(16, bits=0b0010001010000110)
    assert b.popcount() == 5


def test_popcount_64_32():
    b = Bitboard(64, bits=0x5555555555555555)
    assert b.popcount() == 32


def test_popcount_128_66():
    b = Bitboard(128, bits=0x0F0555333FF0030FFFFF33350005333F)
    assert b.popcount() == 66


def test_popcount_64_0():
    b = Bitboard(64)
    assert b.popcount() == 0


def test_xor():
    b = Bitboard(8)
    b.set(4, 7, True)
    b.set(2, 3, True)
    assert (
        b
        ^ Bitboard(
            b.size, bits=0b0000000000000000000000000000000000100000000000000000000000000
        )
    ).bits == 0b1000000000000000000000000000000000000000000000000000000000000


def test_and():
    b = Bitboard(8)
    b.set(4, 7, True)
    b.set(2, 3, True)
    assert (
        b
        & Bitboard(
            b.size, bits=0b0000000000000000000000000000000000100000000000000000000000000
        )
    ).bits == 0b100000000000000000000000000


def test_or():
    b = Bitboard(8)
    b.set(3, 7, True)
    b.set(7, 3, True)
    assert (
        b
        | Bitboard(
            b.size, bits=0b0000000000000000000000000000000000100000000000000000000000000
        )
    ).bits == 0b100000000000000000000000000010000100000000000000000000000000


def test_invert():
    b = Bitboard(8)
    b.set(5, 7, True)
    b.set(3, 2, True)
    b.set(4, 4, True)
    assert (
        ~b
    ).bits == 0b1101111111111111111111111110111111111111111101111111111111111111


def test_hash():
    b = Bitboard(6)
    b.set(4, 5, True)
    b.set(3, 3, True)
    b.set(1, 1, True)
    assert hash(b) == -1957283818685289992


def test_empty():
    b = Bitboard(8)
    assert b.empty()


def test_eq():
    def __set(b: Bitboard):
        b.set(4, 5, True)
        b.set(7, 4, True)
        b.set(8, 4, True)

    b = Bitboard(8)
    b2 = Bitboard(8)
    __set(b)
    __set(b2)
    assert b == b2
    b.set(1, 1, True)
    assert b != b2
    assert b != 3


def test_str():
    assert (
        str(pytest.b)
        == """| | | |·| |
|·| | | | |
| | | | |·|
| | |·| | |
|·| | | | |"""
    )


# ·


def test_minux_one():
    b = Bitboard(6, bits=-1)
    assert b.popcount() == 36


def test_pseudo_rand_values():
    def __count_hot_bits(n: int):
        return len(list(filter(lambda x: x == "1", bin(n))))

    random.seed(23)
    random_bits = random.randint(0, 8 * 8)
    b = Bitboard(8, bits=random_bits)
    assert b.popcount() == __count_hot_bits(random_bits)

    random_bits = random.randint(0, 9 * 9)
    b = Bitboard(9, bits=random_bits)
    assert b.popcount() == __count_hot_bits(random_bits)

    random_bits = random.randint(0, 64 * 64)  # bc why not?
    b = Bitboard(64, bits=random_bits)
    assert b.popcount() == __count_hot_bits(random_bits)


def test_hot_bits_coordinates():
    b = Bitboard(3, bits=0b000110001)
    must_be_positions = [(0, 0), (1, 1), (2, 1)]
    assert b.hot_bits_coordinates() == must_be_positions
    b = Bitboard(6, bits=0b000010100001001000000000000010100001)
    must_be_positions = [(0, 0), (5, 0), (1, 1), (3, 3), (0, 4), (5, 4), (1, 5)]
    assert b.hot_bits_coordinates() == must_be_positions
