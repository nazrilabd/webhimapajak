#!/bin/bash
# =====================================================
# Build script untuk Vercel deployment
# Dijalankan otomatis saat Vercel build
# =====================================================

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Build complete!"
