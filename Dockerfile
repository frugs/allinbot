# Pull base image
FROM ubuntu

# Install python 3.5.2
RUN apt-get update -y && apt-get install python3 python3-pip -y

# Install dependencies
RUN python3 -m pip install -r requirements.txt

# Start bot
CMD python3 main.py

