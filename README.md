# Pumpix
Pumpix is a hardened, opinionated fork of [monopro pixel convert](https://github.com/tsutsuji815/pixel_convert)
to support modern python releases and packages. The application allows for the
rasterisation of images in a minimalistic, easy to use way.

Pumpix doesn't aim to be the best tool for this purpose, rather a simple one
thats easy to enjoy. If you need somthing with a more rounded feature set,
consider [Dithermark](https://app.dithermark.com), its very cool :)

# Installation:
Pumpix requires a python version >= `3.9`.
- add an aplication user with `useradd pumpix -m; su pumpix; cd`
- clone the repository: `git clone https://github.com/Bibostin/pumpix.git; cd pumpix`
- setup a pyenv: `python -m venv venv`
- source the pyenv for package installation `source venv/bin/<APPROPRIATE_ACTIVATE>`
- install the dependencies `pip install -r requirements.txt`
- Modify `app.py` and change the `CONFIG` parameters of the app appropriately:
- run `uwsgi --http 127.0.0.1:<PORT> --master -p 1 -w wsgi:app`
- Enjoy! :)

### Masqerade behind NGINX
To expose the UWSGI process from NGINX, you can use the a simple proxy pass:
```
    location ~ ^/(pumpix|static) {
        proxy_pass http://127.0.0.1:<PORT>;
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
