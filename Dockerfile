FROM centos
LABEL MAINTAINER=sdp.uturn@gmail.com
RUN yum install epel-release -y 
COPY API_testing_framework_with_python_and_robot/ /automation_testing
WORKDIR /automation_testing
CMD ["python" , "Libraries/setup.py"]

