# Penelitian STATISTIK Lab. — kontainer aplikasi
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# LibreOffice TIDAK dibutuhkan (belum ada ekspor .docx di Fase 1).
# numpy/scipy/pandas sudah punya wheel manylinux — tidak perlu compiler.
RUN pip install --no-cache-dir \
        fastapi==0.115.6 \
        "uvicorn[standard]==0.34.0" \
        jinja2==3.1.5 \
        python-multipart==0.0.20 \
        numpy==2.2.1 \
        scipy==1.15.1 \
        pandas==2.2.3 \
        openpyxl==3.1.5 \
        Pillow==13.0.0 \
        pyreadstat==1.2.9

# lapisan berubah — taruh di bawah supaya cache pip tidak kebuang
COPY app/ /app/app/
COPY scripts/ /app/scripts/

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=12s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=4).status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
