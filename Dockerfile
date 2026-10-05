FROM python:3.11-slim
CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0", "--server.port=7860", "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"]