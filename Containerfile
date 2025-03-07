# Pumpix container image
FROM python:3.10

# Build structure
WORKDIR /home/pumpix
RUN groupadd -r pumpix && useradd -r pumpix -g pumpix
COPY --chown=pumpix:pumpix . ./ 
RUN pip3 install -r ./requirements.txt  
RUN apt-get update && apt-get install libgl1  -y # cv2 complains..

# Start
USER pumpix
EXPOSE 8023
CMD ["uwsgi", "--socket", "0.0.0.0:8023", "--wsgi-file", "app.py", "--need-app"]
