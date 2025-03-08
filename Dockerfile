# Gunakan image Python
FROM python:3.9

ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy semua kode
COPY . /app/

# Koleksi static (jika diperlukan)
# RUN python manage.py collectstatic --noinput

# Jalankan aplikasi dengan gunicorn
CMD ["gunicorn", "ctfwiki.wsgi:application", "--bind", "0.0.0.0:8000"]
