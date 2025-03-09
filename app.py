from cv2 import imwrite
from PIL import Image
from threading import Thread
from os import path, listdir, remove
from filetype import guess
from hashlib import md5
from yaml import safe_load
from time import sleep, time
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from pixel import rasterise

app = Flask(
    __name__,
    static_url_path='/pumpix_static/',
    static_folder="pumpix_static")
limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri='memory://',
    strategy='fixed-window-elastic-expiry'
)
with open('config.yaml', 'r') as conf:
    CONFIG = safe_load(conf)
    app.config.update(CONFIG)

if app.config['DEBUG']:
    for key, value in CONFIG.items():
        print(f'{key}:{value}')

if app.config['BEHIND_PROXY']:
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_prefix=1
    )

def with_templates(org_image=None, result_path=None, colors=None, error=None,
    k=None, scale=None, erode=None, blur=None, saturation=None, contrast=None, alpha=None):
    ''' Define a standard means for the app to returm a HTML doc to
    A prospective client. Specific template params bellow are all
    optional, and can be added / called as needed.'''
    return render_template(
        'index.html',
        k=k,
        scale=scale,
        erode=erode,
        blur=blur,
        saturation=saturation,
        contrast=contrast,
        alpha=alpha,
        org_image=org_image,
        result=result_path,
        colors=colors,
        error=error,
        config=CONFIG if app.config['PASS_CONFIG'] else None
    )

def prune_files():
    ''' check ./pumpix_static/results and ./pumpix_static/img for files
    older then those decreed by IMAGE_LIFESPAN, and delete them.'''

    static_img = './pumpix_static/img'
    static_res = './pumpix_static/results'

    # check if we actually want to prune
    if app.config['IMAGE_LIFESPAN'] == -1:
        print('prune disabling: IMAGE_LIFESPAN is -1')
        return

    while True:
        cutoff = time() - app.config['IMAGE_LIFESPAN']
        paths = [path.join(static_img, file) for file in listdir(static_img)]
        paths += [path.join(static_res , file) for file in listdir(static_res)]
        hits = 0
        misses = 0

        # perform the prune
        print(f'prune started: {datetime.now()}')
        for image_path in paths:
            try:
                if path.getmtime(image_path) < cutoff:
                    remove(image_path)
                    hits += 1
                else:
                    misses +=1
            except (PermissionError, FileNotFoundError):
                err = (f'failed to access or find file:{image_path}, skipping.')
                print(err)
        print(f'prune completed: {datetime.now()} hits:{hits} misses:{misses}')
        sleep(app.config['IMAGE_PRUNE_INTERVAL'])



@app.route('/pumpix', methods=['GET'])
@limiter.limit(app.config['RATE_LIMIT'])
def index():
    return with_templates()

@app.route('/pumpix', methods=['POST'])
@limiter.limit(app.config['RATE_LIMIT'])
def post():
    req = request
    img = req.files['image']
    img_path = str(req.form.get('img_path'))
    addr = req.remote_addr

    # check a file has been supplied
    if img:
        # do a quick coarse check the extension is actually an image.
        # fail quickly here for valid clients who make a mistake.
        img_filename = secure_filename(img.filename)
        img_extension = str(path.splitext(img_filename)[1])
        if img_extension not in app.config['UPLOAD_EXTENSIONS']:
            err = f'Invalid file format! (Valid: {app.config["UPLOAD_EXTENSIONS"]})'
            return with_templates(error=err)

        # do a finegrain check the user is being honest with us :) check the
        # file header is to infer the extension, then check validity.
        header = img.stream.read(261)
        header_format = guess(header)
        if not header_format:
            err=f'{img_filename} appears to be corrupted, or missing its file header.'
            return with_templates(error=err)

        header_format = '.' + header_format.extension
        if header_format not in app.config['UPLOAD_EXTENSIONS']:
                err = f'Invalid file format! (Valid: {app.config["UPLOAD_EXTENSIONS"]})'
                return with_templates(error=err)

        # store the original image server side
        img_name = md5(str(datetime.now()).encode('utf-8')).hexdigest()
        img_path = path.join('pumpix_static/img', img_name + img_extension)
        result_path = path.join('pumpix_static/results', img_name + '.png')
        # reseek because were ahead of the stream after fetching the header
        img.stream.seek(0)
        img.save(img_path)

        # reopen with pillow to get access to its image propertys and methods,
        # then if img > dimension_tuple downscale and overwrite.
        with Image.open(img_path) as img_pillow:
            dimension_tuple = (app.config['MAX_IMAGE_WIDTH'], app.config['MAX_IMAGE_HEIGHT'])
            if img_pillow.size > dimension_tuple:
                img_pillow.thumbnail(dimension_tuple, Image.LANCZOS)
                img_pillow.save(img_path)

    # otherwise the user may want to use the previous image
    else:
        # Check if the image path exists on the server
        if not img_path or not path.exists(img_path):
            err = 'No image supplied or existing image has been pruned.'
            return with_templates(error=err)
        # otherwise, its valid, user is using a previous image and we only need
        # to create a result_path, not a img_path.
        img_name = md5(str(datetime.now()).encode('utf-8')).hexdigest()
        result_path = path.join('pumpix_static/results', img_name + '.png')

    # pull the forms keys into specific values sanely
    k =  int(req.form['k'])
    scale = int(req.form['scale'])
    blur = int(req.form['blur'])
    erode = int(req.form['erode'])
    saturation = float(req.form['saturation'])
    contrast = float(req.form['contrast'])
    alpha = req.form.get('alpha', False, bool)

    if app.config['DEBUG']:
        msg = (
            f'{addr}: {img_path}\n'
            f'{addr}: {result_path}\n'
            f'{addr}: {req.form}\n'
        )
        print(msg)

    # convert the image to pixel art.
    img_res, colors = rasterise(
        img_path,
        k=k,
        scale=scale,
        blur=blur,
        erode=erode,
        saturation=saturation,
        contrast=contrast,
        alpha=alpha
    )

    # write the output file to the results folder and return the end result,
    # colors (if applicable) and path to the original image for reprocessing
    imwrite(result_path, img_res)
    return with_templates(
        org_image=img_path,
        result_path=result_path,
        colors=colors,
        k=k,
        scale=scale,
        erode=erode,
        blur=blur,
        saturation=saturation,
        contrast=contrast,
        alpha=alpha
    )

@app.errorhandler(400)
def form_error(e):
    err = 'submited settings appear malformed, please try again.'
    return with_templates(error=err), 400

@app.errorhandler(404)
def not_found(e):
    err = 'Unable to find the requested file!'
    return with_templates(error=err), 404

@app.errorhandler(413)
def error_file_size(e):
    MAX_MB = app.config['MAX_IMAGE_SIZE'] / (1024 * 1024)
    err = f'File size exceeds {MAX_MB}MB!'
    return with_templates(error=err), 413

@app.errorhandler(429)
def rate_limited(e):
    err = 'You have exceeded the rate limit! please be patient.'
    return with_templates(error=err), 429

# setup our cleanup thread
cleanup_thread = Thread(target=prune_files)
cleanup_thread.daemon = True
cleanup_thread.start()

# if called directly, use flask
if __name__ == '__main__':
    app.run(use_reloader=False)
# if indirectly, use uwsgi
else:
    application = app
