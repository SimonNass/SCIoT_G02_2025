FROM python:2.7

WORKDIR /app

# Install required packages
RUN sudo curl -kL dexterindustries.com/update_grovepi | bash \
    pip install python-periphery

# Copy application code
COPY ./room_unit_gateway .

# Make sure the entry point can be executed
RUN chmod +x main.py

CMD ["python", "main.py"]