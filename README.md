# Pumpix
Pumpix is a hardened, opinionated fork of [monopro pixel convert](https://github.com/tsutsuji815/pixel_convert)
to support modern python releases and packages. The application allows for the
rasterisation of images in a minimalistic, easy to use way.

Pumpix doesn't aim to be the best tool for this purpose, rather a simple one 
thats easy to enjoy. If you need somthing with a more rounded feature set,
consider [Dithermark](https://app.dithermark.com), its very cool :)    

# Installation:
Pumpix requires a python version >= `3.9`. Pumpix also requires a redis
- Python > 3.9 
- Redis Server

- clone the repository: `git clone URLHERE; cd pumpix`
- setup a pyenv: `python -m venv`
- source the pyenv for package installation `source venv/bin/activate`
- install the dependencies `pip install -r requirements.txt`
- run `uwsgi --http 127.0.0.1:8023 --master -p 1 -w wsgi:app`
- Enjoy! :)

# Credits:
- Contact me at bibostin@coenin.co.uk or via issue for requests / bugs 
- [Tsutsuji](https://monopro.org), for the original Flask program.
- Lax for the cute name.
