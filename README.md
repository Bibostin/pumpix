# Pumpix
Pumpix is a hardened, opinionated fork of [monopro pixel convert](https://github.com/tsutsuji815/pixel_convert)
to support modern python releases and packages. The application allows for the
rasterisation of images in a minimalistic, easy to use way.

![Example](pumpix_static/oni.png)

You can find a reference deployment of the app [here](https://www.coenin.co.uk/pumpix)

Pumpix doesn't aim to be the best tool for this purpose, rather a simple one
thats easy to enjoy. If you need somthing with a more rounded feature set,
consider [Dithermark](https://app.dithermark.com), its very cool :)


# Installation:

### Run locally (localhost):
- Pumpix should run anywhere python does, however it requires a version >= `3.9`.
- Clone the repository: `git clone https://github.com/Bibostin/pumpix.git; cd pumpix`
- Setup a pyenv: `python -m venv venv`
- Source the pyenv for package installation `source venv/bin/<APPROPRIATE_ACTIVATE>`
- Install the dependencies `pip install -r requirements.txt`
- Modify `config.yaml` to change the parameters of the app to preference
- Run `uwsgi --http-socket 127.0.0.1:8023 --wsgi-file app.py --need-app`
- Go to `http://127.0.0.1:8023/pumpix` in your browser of choice and enjoy! :)

### Install locally (production)
- As the `USER` you intend to run pumpix and your webserver with (typically `nginx`):
- Clone the repo as `USER`: `git clone https://github.com/Bibostin/pumpix.git; cd pumpix`
- Setup a pyenv: `python -m venv venv`
- Source the pyenv for package installation `source venv/bin/<APPROPRIATE_ACTIVATE>`
- Install the dependencies `pip install -r requirements.txt`
- Modify `config.yaml` to change the parameters of the app to preference
- run `uwsgi --socket 127.0.0.1:8023 --wsgi-file app.py --need-app`
- A very basic, example sytemd unit exists at `/pumpix_static/pumpix.service`,
  it requires you to write the path of your pumpix install to function.

### Install as a container (production)
- Clone the repository to the orchestrator with `git clone https://github.com/Bibostin/pumpix.git`
- Modify `config.yaml` to change the parameters of the app to preference
- Navigate out of the repo and build a local image with `podman build pumpix/ --tag pumpix`
- Run `podman run  --name pumpix -d -p 8023:8023/tcp pumpix` to initiate the container,
  and if desired, use the systemd unit found at `/pumpix_static/pumpix-container.service`
  on the orchestrator.

- A more advanced, K8/3/s deployment is left to user preference.

### Masqerade Behind NGINX (reverse proxy):
I have a preference for exposing web apps on my domain as sub-sites rather
then as seperate web servers, or `app.<domain>.<tld>` to simplify TLS deployment
(I'm not a fan of wildcard certs either) this guide is informed by that choice.

This section is valid for both a direct install, and a container, in both cases
pumpix exposes itself for proxying via a wsgi socket.

- In app.py, make sure `BEHIND_PROXY` is set to `True`
- Ensure pumpix is running (either in a container or locally.)
- Add the following location definition to your nginx configuration.
```
    # pass pumpix
    location ~ ^/pumpix {
        include uwsgi_params;
        uwsgi_pass uwsgi://<127.0.0.1||container-ip>:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```
- Restart nginx with `systemctl restart nginx`
- Enjoy at `http<s>://<yourdomain>.<tld>/pumpix`!

# Credits:
- Contact me at bibostin@coenin.co.uk or via issue for requests / bugs
- [Tsutsuji](https://monopro.org), for the original Flask program.
- Lax for the cute name.
