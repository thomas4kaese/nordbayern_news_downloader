FROM alpine:edge

# install chromium and chromedriver
RUN apk add --no-cache \
    dumb-init \
    chromium \
    chromium-chromedriver

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip3 install selenium

# for external access
# run chromedriver under dumb-init to handle signals correctly
#EXPOSE 4444
#ENTRYPOINT ["/usr/bin/dumb-init", "--"]
#CMD ["chromedriver", "--port=4444", "--whitelisted-ips="]

WORKDIR /app
CMD ["python3", "/app/nn_chrome.py"]