# Pumpix
Pumpix is a hardened, opinionated fork of [monopro pixel convert](https://github.com/tsutsuji815/pixel_convert)
to support modern python releases and packages. The application allows for the
rasterisation of images in a minimalistic, easy to use way.

Pumpix doesn't aim to be the best tool for this purpose, rather a simple one
thats easy to enjoy. If you need somthing with a more rounded feature set,
consider [Dithermark](https://app.dithermark.com), its very cool :)

# Installation:
While Pumpix is *pretty much* distribution agnostic, it does require a python
version >= `3.9`. ensure you match this with `python -V`.

### Expose directly (localhost):
- Clone the repository: `git clone https://github.com/Bibostin/pumpix.git; cd pumpix`
- Setup a pyenv: `python -m venv venv`
- Source the pyenv for package installation `source venv/bin/<APPROPRIATE_ACTIVATE>`
- Install the dependencies `pip install -r requirements.txt`
- Modify `app.py` and change the `CONFIG` parameters of the app appropriately:
- Run `uwsgi --http 127.0.0.1:8023 --master -p 1 -w wsgi:app`
- Go to `http://127.0.0.1:8023` in your browser of choice and enjoy! :)

### Behind NGINX (reverse proxy):
Running Pumpix in this manner implies, you want to use it for a production
use case. Thanks for liking it so much! but keep in mind, your milage may
vary, and the bellow guide should only be taken as a template.

I have a preference for exposing web apps on my domain as sub-sites rather
then as seperate web servers, or `app.<domain>.<tld>` to simplify TLS deployment,
this guide is informed by that choice.

#### Setup Pumpix

- As the `USER` you intend to run nginx with (typically `nginx`):
- Clone the repo as `USER`: `git clone https://github.com/Bibostin/pumpix.git; cd pumpix`
- Setup a pyenv: `python -m venv venv`
- Source the pyenv for package installation `source venv/bin/<APPROPRIATE_ACTIVATE>`
- Install the dependencies `pip install -r requirements.txt`
- Modify `app.py` and change the `CONFIG` parameters of the app appropriately:
- run `uwsgi --socket 127.0.0.1:8023 --master -p 1 -w wsgi:app`

#### Setup Nginx

Add the following location definition to your nginx configuration.
```
    # pass pumpix
    location ~ ^/pumpix {
        include uwsgi_params;
        uwsgi_pass uwsgi://127.0.0.1:8023;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

# Credits:
- Contact me at bibostin@coenin.co.uk or via issue for requests / bugs
- [Tsutsuji](https://monopro.org), for the original Flask program.
- Lax for the cute name.
