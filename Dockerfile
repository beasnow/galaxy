FROM python:3.6
ADD . /galaxy
WORKDIR  /galaxy
RUN pip install -r requirement.txt
CMD python ./main.py