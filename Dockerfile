FROM centos
LABEL MAINTAINER=sdp.uturn@gmail.com
RUN yum install epel-release -y && yum install python-pip -y
COPY . /automation_testing/
WORKDIR /automation_testing
RUN pip install -r Config/requirements.txt
CMD ["python" , "Libraries/setup.py"]

