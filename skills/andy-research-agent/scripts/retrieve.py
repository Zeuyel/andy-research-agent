#!/usr/bin/env python3
"""Compatibility entry point for curated knowledge retrieval (not the raw corpus)."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('retrieve_knowledge.py')), run_name='__main__')
