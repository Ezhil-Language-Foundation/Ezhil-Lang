FROM fedora
COPY ./ezhili-0.90.1-1.noarch.rpm /home/
WORKDIR /home
RUN dnf install -y \
python-pip 
RUN pip install \
open-tamil \
argparse 
RUN dnf install -y ezhili-0.90.1-1.noarch.rpm
ENTRYPOINT ["/usr/bin/ezhili"]
