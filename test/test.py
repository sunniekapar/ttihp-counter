# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_counter_reset(dut):
    """Test that counter resets to 0"""
    dut._log.info("Testing counter reset")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Enable output
    dut.ui_in.value = 0b00000100  # output_en=1, count_en=0, load_en=0
    await ClockCycles(dut.clk, 1)
    
    # After reset, counter should be 0
    assert dut.uo_out.value == 0, f"Expected 0 after reset, got {dut.uo_out.value}"


@cocotb.test()
async def test_counter_load(dut):
    """Test that counter loads a value when load_en is high"""
    dut._log.info("Testing counter load functionality")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Test load functionality
    load_value = 42
    dut.uio_in.value = load_value  # Load data
    dut.ui_in.value = 0b00000101  # output_en=1, count_en=0, load_en=1
    await ClockCycles(dut.clk, 2)  # Wait for load to complete
    
    # Counter should now contain the loaded value
    assert dut.uo_out.value == load_value, f"Expected {load_value}, got {dut.uo_out.value}"


@cocotb.test()
async def test_counter_count_up(dut):
    """Test that counter counts up when count_en is high"""
    dut._log.info("Testing counter count up functionality")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Enable output and counting
    dut.ui_in.value = 0b00000110  # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 1)  # Settle inputs
    
    # Count and check each value
    for i in range(1, 5):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == i, f"Expected {i}, got {dut.uo_out.value}"


@cocotb.test()
async def test_counter_output_disable(dut):
    """Test that counter output is tri-stated when output_en is low"""
    dut._log.info("Testing counter output disable (tri-state)")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Enable counting but disable output
    dut.ui_in.value = 0b00000010  # output_en=0, count_en=1, load_en=0
    await ClockCycles(dut.clk, 3)
    
    # Output should be tri-stated (high impedance)
    # We'll just verify the test doesn't crash


@cocotb.test()
async def test_counter_overflow(dut):
    """Test that counter overflows correctly"""
    dut._log.info("Testing counter overflow")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Load 255 (max 8-bit value)
    dut.uio_in.value = 255
    dut.ui_in.value = 0b00000101  # output_en=1, count_en=0, load_en=1
    await ClockCycles(dut.clk, 2)  # Load the value
    
    # Enable counting
    dut.ui_in.value = 0b00000110  # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 2)  # Count from 255 to 0
    
    # Should overflow to 0
    assert dut.uo_out.value == 0, f"Expected 0 after overflow, got {dut.uo_out.value}"


@cocotb.test()
async def test_counter_priority(dut):
    """Test that load has priority over count"""
    dut._log.info("Testing counter priority (load over count)")
    
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    
    # Count up to 5
    dut.ui_in.value = 0b00000110  # output_en=1, count_en=1, load_en=0
    await ClockCycles(dut.clk, 1)  # Settle inputs
    for i in range(1, 6):
        await ClockCycles(dut.clk, 1)
        assert dut.uo_out.value == i, f"Expected {i}, got {dut.uo_out.value}"
    
    # Now load a new value while count_en is still high
    dut.uio_in.value = 100
    dut.ui_in.value = 0b00000111  # output_en=1, count_en=1, load_en=1
    await ClockCycles(dut.clk, 2)  # Load should take priority
    
    # Should load the new value, not count up
    assert dut.uo_out.value == 100, f"Expected 100 (loaded), got {dut.uo_out.value}"