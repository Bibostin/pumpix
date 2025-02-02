import os
import cv2
import hashlib
import filetype
from pixel import rasterise
from PIL import Image
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

CONFIG = {
    'VERSION': '1.0.0',
    'DEBUG': True,
    'PASS_CONFIG': True, 
    'BEHIND_PROXY': True,
    'GET_LIMIT':  '500/day; 200/hour; 50/minute',
    'POST_LIMIT': '100/day; 20/hour; 10/minute',
    'UPLOAD_EXTENSIONS': ['.png', '.jpg', '.jpeg'],
    'MAX_CONTENT_LENGTH': 1024 * 1024 * 2, # 2097152B, 2MB.
    'MAX_IMAGE_DIMENSIONS': (1024, 1024), # 1024 * 1024 px
}

app = Flask(__name__)
app.config.update(CONFIG)
if app.config['BEHIND_PROXY']:
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1, 
        x_host=1, 
        x_prefix=1
    )
if app.config['DEBUG']:                                                         
    print(f'config: {CONFIG}')

limiter = Limiter(
    get_remote_address, 
    app=app, 
    storage_uri='memory://', 
    strategy='fixed-window-elastic-expiry'
)

# Define a standard way for the app to return a  HTML document to the client,
# within which, specific Templates can be added as needed in the bellow code.
def return_with_templates(
    org_img=None, result_path=None, colors=None, error=None, k=None, 
    scale=None, erode=None, saturation=None, contrast=None, dither=None,
    alpha=None
):
    return render_template(
        'index.html',
        k=k,                                                                    
        scale=scale,                                                            
        erode=erode,                                                            
        saturation=saturation,                                                  
        contrast=contrast,                                                      
        dither=dither,                                                          
        alpha=alpha, 
        org_image=org_img,
        result=result_path,
        colors=colors,
        error=error,
        config=CONFIG if app.config['PASS_CONFIG'] else None
    )

# Default route
@app.route('/', methods=['GET'])
@limiter.limit(app.config['GET_LIMIT'])
def index():
    return return_with_templates()

# Respond to a POST request.
@app.route('/', methods=['POST'])
@limiter.limit(app.config['POST_LIMIT'])
def post():
    req = request
    img = req.files['image']
    addr = req.remote_addr

    # check a file has been supplied
    if not img:
        err = 'No image supplied'
        return return_with_templates(error=err)
    img_filename = secure_filename(img.filename)

    # do a quick coarse check the extension is actually an image. fail quickly
    # here for valid clients who make a mistake.
    img_extension = str(os.path.splitext(img_filename)[1])
    if not img_extension in app.config['UPLOAD_EXTENSIONS']:
        err = f'Invalid file format! (Valid: {app.config["UPLOAD_EXTENSIONS"]})'
        return return_with_templates(error=err)

    # do a finegrain check the user is being honest with us :) check the
    # file header is to infer the extension, then check validity.
    header = img.stream.read(261)
    header_format = filetype.guess(header)
    if not header_format:
        err=f'{img_filename} appears to be corrupted, or missing its file header.'
        return return_with_templates(error=err)

    header_format = '.' + header_format.extension
    if not header_format in app.config['UPLOAD_EXTENSIONS']:
            err = f'Invalid file format! (Valid: {app.config["UPLOAD_EXTENSIONS"]})'
            return return_with_templates(error=err)

    # store the image serverside
    img_name = hashlib.md5(str(datetime.now()).encode('utf-8')).hexdigest()
    img_path = os.path.join('static/img', img_name + img_extension)
    result_path = os.path.join('static/results', img_name + '.png')
    img.stream.seek(0)
    img.save(img_path)

    # reopen with pillow to get access to its image propertys and methods,
    # then if img > MAX_IMAGE_DIMENSIONS, downscale and overwrite.
    with Image.open(img_path) as img_pillow:
        if img_pillow.size > app.config['MAX_IMAGE_DIMENSIONS']:
            img_pillow.thumbnail(app.config['MAX_IMAGE_DIMENSIONS'], Image.LANCZOS)
            img_pillow.save(img_path)

    # pull the forms keys into specific values
    k =  int(req.form['k'])
    scale = int(req.form['scale'])
    blur = int(req.form['blur'])
    erode = int(req.form['erode'])
    saturation = float(req.form['saturation'])
    contrast = float(req.form['contrast'])
    dither = req.form.get('dither', False, bool)
    alpha = req.form.get('alpha', False, bool)
    if app.config['DEBUG']:
        msg = (
            f'{addr}: {img_filename}\n'
            f'{addr}: {img_path}\n'
            f'{addr}: {result_path}\n'
            f'{addr}: {req.form}\n'
            f'{addr}: {k} {scale} {blur} {erode} {saturation} {contrast} {dither} {alpha}'
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
        dither=dither,
        alpha=alpha
    )

    # write the output file to the results folder and return the end result,
    # colors (if applicable) and path to the original image for reprocessing
    cv2.imwrite(result_path, img_res)
    return return_with_templates(
        org_img=img_path,
        result_path=result_path,
        colors=colors,
        k=k,
        scale=scale,
        erode=erode,
        saturation=saturation,
        contrast=contrast,
        dither=dither,
        alpha=alpha
    )

# Form malformed
@app.errorhandler(400)
def form_error(e):
    err = 'submited settings appear malformed, please try again.'
    return return_with_templates(error=err), 400

# GET URI not found
@app.errorhandler(404)
def not_found(e):
    err = 'Unable to find the requested file!'
    return return_with_templates(error=err), 404

# file exceeded MAX_CONTENT_LENGTH
@app.errorhandler(413)
def error_file_size(e):
    MAX_MB = app.config['MAX_CONTENT_LENGTH'] / (1024 * 1024)
    err = 'File size exceeds {MAX_MB}MB!'
    return return_with_templates(error=err), 413

# Rate limit exceeded
@app.errorhandler(429)
def form_error(e):
    err = 'You have exceeded the rate limit! please be patient.'
    return return_with_templates(error=err), 429

if __name__ == '__main__':
    app.run()
