#!/usr/bin/env python
import os
import requests
import requests.utils
import json
from urllib.parse import urljoin

import click

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("url")
@click.option("--username", prompt=True)
@click.option('--password', prompt=True, confirmation_prompt=False,
              hide_input=True)
def login(url, username, password):
    url = urljoin(url, "/hub/login")

    payload = {"username": username, "password": password}
    response = requests.post(url, payload, verify=False, allow_redirects=False)

    if response.status_code == 302:
        with open(os.path.expanduser("~/.remoteapprest"), "w") as f:
            f.write("{}\n".format(url))
            f.write("{}\n".format(username))
            cookies = requests.utils.dict_from_cookiejar(response.cookies)
            for k, v in cookies.items():
                f.write("{}={}\n".format(k, v))

# -------------------------------------------------------------------------


def _get_auth_info():
    with open(os.path.expanduser("~/.remoteapprest"), "r") as f:
        lines = f.readlines()

    url = lines[0].strip()
    username = lines[1].strip()
    cookies = {}
    for line in lines[2:]:
        k, v = line.split('=', 1)
        cookies[k.strip()] = v.strip()

    return url, username, cookies


@cli.group()
def app():
    pass


@app.command()
def available():
    url, username, cookies = _get_auth_info()

    request_url = urljoin(url,
                          "/user/{}/api/v1/applications/".format(username))
    response = requests.get(request_url, cookies=cookies, verify=False)

    data = json.loads(response.content.decode("utf-8"))
    for item_id in data["items"]:
        request_url = urljoin(url,
                              "/user/{}/api/v1/applications/{}/".format(
                                  username,
                                  item_id))
        response = requests.get(request_url, cookies=cookies, verify=False)
        app_data = json.loads(response.content.decode("utf-8"))
        print("{}: {}".format(
            item_id, app_data["image"]
        ))


@app.command()
@click.argument("identifier")
def start(identifier):
    url, username, cookies = _get_auth_info()

    request_url = urljoin(url,
                          "/user/{}/api/v1/containers/".format(username))

    payload = json.dumps(dict(
        mapping_id=identifier
    ))

    response = requests.post(request_url, payload, cookies=cookies,
                             verify=False)
    if response.status_code == 201:
        location = response.headers["Location"]
        print(location)


@app.command()
@click.argument("identifier")
def stop(identifier):
    url, username, cookies = _get_auth_info()

    request_url = urljoin(url,
                          "/user/{}/api/v1/containers/{}/".format(
                              username,
                              identifier))
    response = requests.delete(request_url, cookies=cookies, verify=False)
    print(response.status_code)


@app.command()
def running():
    url, username, cookies = _get_auth_info()

    request_url = urljoin(url,
                          "/user/{}/api/v1/containers/".format(
                              username))
    response = requests.get(request_url, cookies=cookies, verify=False)
    data = json.loads(response.content.decode("utf-8"))
    for item_id in data["items"]:
        request_url = urljoin(url,
                              "/user/{}/api/v1/containers/{}/".format(
                                  username,
                                  item_id))
        response = requests.get(request_url, cookies=cookies, verify=False)
        app_data = json.loads(response.content.decode("utf-8"))
        print("{}: {}".format(
            item_id, app_data["image_name"]
        ))


def main():
    cli(obj={})


if __name__ == '__main__':
    main()
