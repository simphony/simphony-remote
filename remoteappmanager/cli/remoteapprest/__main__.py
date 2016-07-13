#!/usr/bin/env python
import sys
import os
import requests
import requests.utils
import json
from urllib.parse import urljoin

import click

# We silence the insecure requests warnings we get for using a
# self-signed certificate.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)


class Credentials:
    """Data class to hold the credentials extracted from the credential file.
    """
    def __init__(self, url, username, cookies):
        self.url = url
        self.username = username
        self.cookies = cookies

    @classmethod
    def from_file(cls, credentials_file):
        """Extracts the authorization info from the credentials file.
        Returns a tuple with url, username, and a dict of credentials
        cookies"""
        with open(credentials_file, "r") as f:
            lines = f.readlines()

        url = lines[0].strip()
        username = lines[1].strip()
        cookies = {}
        for line in lines[2:]:
            k, v = line.split('=', 1)
            cookies[k.strip()] = v.strip()

        return cls(url, username, cookies)

    def write(self, credentials_file):
        """Stores the credentials in a credentials file."""
        with open(credentials_file, "w") as f:
            f.write("{}\n".format(self.url))
            f.write("{}\n".format(self.username))
            for k, v in self.cookies.items():
                f.write("{}={}\n".format(k, v))


class RemoteAppRestContext:
    """The click context passed around."""
    credentials_file = None
    credentials = None


@click.group()
@click.option("--credentials-file",
              default=os.path.expanduser("~/.remoteapprest"),
              help="Specify a different credentials file.")
@click.pass_context
def cli(ctx, credentials_file):
    """Command line interface to start, stop, and inquire applications
    on the remote application server."""
    ctx.obj.credentials_file = credentials_file
    try:
        ctx.obj.credentials = Credentials.from_file(credentials_file)
    except IOError:
        ctx.obj.credentials = None


@cli.command()
@click.argument("url")
@click.option("--username", prompt=True)
@click.option('--password',
              prompt=True,
              confirmation_prompt=False,
              hide_input=True)
@click.pass_context
def login(ctx, url, username, password):
    """Performs login on the remote server at the specified URL."""
    login_url = urljoin(url, "/hub/login")

    payload = {"username": username, "password": password}

    # Unfortunately, jupyterhub handles the afterlogin with an immediate
    # redirection, meaning that we have to check for a 302 and prevent
    # redirection in order to capture the cookies.
    try:
        response = requests.post(login_url, payload, verify=False,
                                 allow_redirects=False)
    except Exception as e:
        print("Could not perform request. {}".format(e))
        sys.exit(1)

    if response.status_code == 302:
        cookies_dict = requests.utils.dict_from_cookiejar(response.cookies)
        cred = Credentials(url, username, cookies_dict)
        cred.write(ctx.obj.credentials_file)
    else:
        print("Failed to perform login. Server replied with error: {}".format(
            response.status_code))
        sys.exit(1)

# -------------------------------------------------------------------------


@cli.group()
@click.pass_context
def app(ctx):
    """Various subcommands to inquire the remote server."""
    if ctx.obj.credentials is None:
        raise click.ClickException("Missing credentials. "
                                   "Use the login command to authenticate.")
    pass


@app.command()
@click.pass_context
def available(ctx):
    cred = ctx.obj.credentials
    url, username, cookies = cred.url, cred.username, cred.cookies

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
@click.pass_context
def start(ctx, identifier):
    """Starts a container for application identified by IDENTIFIER."""
    cred = ctx.obj.credentials
    url, username, cookies = cred.url, cred.username, cred.cookies

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
@click.pass_context
def stop(ctx, identifier):
    """Stop a container identified by IDENTIFIER"""
    cred = ctx.obj.credentials
    url, username, cookies = cred.url, cred.username, cred.cookies

    request_url = urljoin(url,
                          "/user/{}/api/v1/containers/{}/".format(
                              username,
                              identifier))
    response = requests.delete(request_url, cookies=cookies, verify=False)
    print(response.status_code)


@app.command()
@click.pass_context
def running(ctx):
    """Shows the currently running containers."""
    cred = ctx.obj.credentials
    url, username, cookies = cred.url, cred.username, cred.cookies

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
    cli(obj=RemoteAppRestContext())


if __name__ == '__main__':
    main()
