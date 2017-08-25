FROM docker.io/fedora
MAINTAINER Buvanesh Kumar <linuxsbk@gmail.com>

RUN dnf update -y; dnf install -y xorg-x11-twm \
                   tigervnc-server \
                   xterm xulrunner \
                   dejavu-sans-fonts  \
                   dejavu-serif-fonts \
		   python-gobject \
                   xdotool \
		   gtk+ \
		   gtksourceview3 \
		   webkitgtk3 \
		   lohit-tamil-fonts.noarch \
           	   samyak-tamil-fonts.noarch 

RUN dnf install -y python-pip

RUN pip install open-tamil ezhil argparse; dnf clean all

COPY ezhuthi-0.99-1.noarch.rpm .

RUN rpm -ivh ezhuthi-0.99-1.noarch.rpm

# Add the xstartup file into the image and set the default password.
RUN mkdir /root/.vnc
ADD ./xstartup /root/.vnc/
RUN chmod -v +x /root/.vnc/xstartup
RUN echo ezhil | vncpasswd -f > /root/.vnc/passwd
RUN chmod -v 600 /root/.vnc/passwd

RUN sed -i '/\/etc\/X11\/xinit\/xinitrc-common/a [ -x /usr/bin/ezhuthi ] && /usr/bin/ezhuthi &' /etc/X11/xinit/xinitrc

EXPOSE 5901

CMD    ["vncserver", "-fg" ]
