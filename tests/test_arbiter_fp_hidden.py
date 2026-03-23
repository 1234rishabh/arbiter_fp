from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, NextTimeStep
from cocotb_tools.runner import get_runner


def expected_grant(req):
    if req & 0b1000:
        return 0b1000
    elif req & 0b0100:
        return 0b0100
    elif req & 0b0010:
        return 0b0010
    elif req & 0b0001:
        return 0b0001
    else:
        return 0b0000


@cocotb.test()
async def fixed_priority_arbiter_test(dut):

    # Start clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start(start_high=False))

    dut.req.value = 0
    await RisingEdge(dut.clk)

    # 🔥 Exhaustive test
    for req in range(16):

        await NextTimeStep()   # ✅ exit ReadOnly safely
        dut.req.value = req

        await RisingEdge(dut.clk)
        await ReadOnly()

        actual = int(dut.grant.value)
        expected = expected_grant(req)

        assert actual == expected, (
            f"[EXHAUSTIVE FAIL] req={req:04b}, expected={expected:04b}, got={actual:04b}"
        )

        assert (actual & (actual - 1)) == 0, (
            f"[ONE-HOT FAIL] req={req:04b}, grant={actual:04b}"
        )

    # 🔥 Random test
    for _ in range(50):

        await NextTimeStep()   # ✅ critical
        req = random.randint(0, 15)
        dut.req.value = req

        await RisingEdge(dut.clk)
        await ReadOnly()

        actual = int(dut.grant.value)
        expected = expected_grant(req)

        assert actual == expected, (
            f"[RANDOM FAIL] req={req:04b}, expected={expected:04b}, got={actual:04b}"
        )


def test_fixed_priority_arbiter_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    sources = [proj_path / "sources/fpa.sv"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fixed_priority_arbiter",
        always=True,
    )

    runner.test(
        hdl_toplevel="fixed_priority_arbiter",
        test_module="test_arbiter_fp_hidden"
    )
from __future__ import annotations

import os
import random
from pathlib import Path

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, NextTimeStep
from cocotb_tools.runner import get_runner


def expected_grant(req):
    if req & 0b1000:
        return 0b1000
    elif req & 0b0100:
        return 0b0100
    elif req & 0b0010:
        return 0b0010
    elif req & 0b0001:
        return 0b0001
    else:
        return 0b0000


@cocotb.test()
async def fixed_priority_arbiter_test(dut):

    # Start clock
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start(start_high=False))

    dut.req.value = 0
    await RisingEdge(dut.clk)

    # Exhaustive test
    for req in range(16):

        await NextTimeStep()
        dut.req.value = req

        await RisingEdge(dut.clk)
        await ReadOnly()

        actual = int(dut.grant.value)
        expected = expected_grant(req)

        assert actual == expected, (
            f"[EXHAUSTIVE FAIL] req={req:04b}, expected={expected:04b}, got={actual:04b}"
        )

        assert (actual & (actual - 1)) == 0, (
            f"[ONE-HOT FAIL] req={req:04b}, grant={actual:04b}"
        )

    # Random test
    for _ in range(50):

        await NextTimeStep()
        req = random.randint(0, 15)
        dut.req.value = req

        await RisingEdge(dut.clk)
        await ReadOnly()

        actual = int(dut.grant.value)
        expected = expected_grant(req)

        assert actual == expected, (
            f"[RANDOM FAIL] req={req:04b}, expected={expected:04b}, got={actual:04b}"
        )


def test_fixed_priority_arbiter_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent
    sources = [proj_path / "sources/fpa.sv"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fixed_priority_arbiter",
        always=True,
    )

    runner.test(
        hdl_toplevel="fixed_priority_arbiter",
        test_module="test_arbiter_fp_hidden"
    )
