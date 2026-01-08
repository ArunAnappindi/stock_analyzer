#!/usr/bin/env python3
"""
Main entry point for the Stock Analyzer application.

Usage:
    python main.py <TICKER>
    python main.py AAPL --interval 15m
    python main.py TSLA --output json
"""

import sys
from src.cli import analyze_stock

if __name__ == '__main__':
    # Run the CLI directly with the analyze command
    analyze_stock()
