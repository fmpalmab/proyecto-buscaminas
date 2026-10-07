"""Pruebas unitarias para el CLI de Buscaminas."""

import pytest
from buscaminas.cli import main


def test_cli_eval():
    exit_code = main(["--eval", "--eval-games", "20", "--size", "4", "--mines", "0.1"])
    assert exit_code == 0


def test_cli_auto_ascii():
    exit_code = main(["--auto-ascii", "--size", "4", "--mines", "0.1"])
    assert exit_code == 0
