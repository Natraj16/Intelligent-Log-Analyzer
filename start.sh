#!/bin/bash

echo "============================================================"
echo "Intelligent Log Analyzer"
echo "============================================================"
echo ""
echo "Starting Flask application..."
echo "Opening http://localhost:5000 in your browser..."
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

PYTHONPATH=src python src/app.py
