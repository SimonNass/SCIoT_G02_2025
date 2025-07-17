FROM yikaiyang/grovepi

WORKDIR /app

ADD room_pi_requirements.txt .
RUN python3 -m pip install -r room_pi_requirements.txt 

# Copy application code
COPY ./room_unit_gateway .

# Make sure the entry point can be executed
RUN chmod +x main.py

ENTRYPOINT ["python3", "main.py"]
CMD ["configs_dir/manual_configs/config_pi_and_ardoino.ini", "password"]
