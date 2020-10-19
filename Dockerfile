FROM python:3.8-slim

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

ADD https://storage.googleapis.com/kubernetes-release/release/v1.19.3/bin/linux/amd64/kubectl /usr/local/bin/kubectl
RUN chmod +x /usr/local/bin/kubectl

ARG user=operator
ARG group=operator
ARG uid=1000
ARG gid=1000
ARG HOME=/home/operator

RUN mkdir -p $HOME \
    && chown ${uid}:${gid} $HOME \
    && groupadd -g ${gid} ${group} \
    && useradd -d "$_HOME" -u ${uid} -g ${gid} -m -s /bin/bash ${user}

ENV KUBECONFIG $HOME/.kube/config

COPY operator.py $HOME/src
CMD kopf run $HOME/src/operator.py
