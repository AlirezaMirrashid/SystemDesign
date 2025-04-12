FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install flask redis flask-cors
EXPOSE 5001 5002
# Default SERVICE is set to "write". It can be overridden in docker-compose.
ENV SERVICE=write
CMD ["sh", "-c", "if [ \"$SERVICE\" = 'write' ]; then python write_service.py; else python read_service.py; fi"]
