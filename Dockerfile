FROM continuumio/miniconda3

WORKDIR /app

# Install Prophet via Conda (this includes pre-compiled C++ binaries and numpy!)
RUN conda install -c conda-forge prophet==1.1.5 "numpy<2.0" python=3.12 -y

# Copy remaining requirements and install via pip (pandas, psycopg2-binary)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose Streamlit's default port
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
