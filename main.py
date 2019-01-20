import flask
import zipfile
import io
import codecs

import process

page="""
<form method="post" enctype="multipart/form-data">
        <input type="file" name="file" id="file">
        <input type="submit">
</form>
"""

def create_zipfile(l):
    data=io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for name, content in l:
            z.writestr(name, content)
    data.seek(0)
    return data


def hello_handler(request):
    return 'Hello, it works!'


def upload_handler(request):
    if request.method == "POST":
        if 'file' not in request.files:
            return 'NO FILE UPLOAD'
        binary_input = request.files['file']
        #text_input = io.TextIOWrapper(binary_input,errors='ignore')
        text_input = codecs.getreader('utf-8')(binary_input, errors='ignore')
        l = process.process_content(text_input.readlines())
        zipfile = create_zipfile(l)
        return flask.send_file(
                zipfile,
                mimetype='application/zip',
                as_attachment=True,
                attachment_filename='processed.zip'
                )
    else:
        return page
