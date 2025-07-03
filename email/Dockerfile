FROM ubuntu:20.04

RUN apt update

RUN apt upgrade -y

RUN apt install postfix vim dnsutils iputils-ping telnet -y

COPY postfix/main.cf /etc/postfix/main.cf


# Add User
#RUN useradd -c 'User Bob' -m -s /bin/false bob

# Set user passord
#RUN echo -e "pwd123" | passwd bob

CMD ["postfix", "start-fg"]