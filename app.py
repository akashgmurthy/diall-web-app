import os
import boto3
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask import Flask, request, url_for


aws_access_key_id = 'AKIATRKPRG7S6PL6P2UJ'
aws_secret_access_key = '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'

# S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


# Firebase auth
cred = credentials.Certificate("/Users/akashganesamurthy/diall-python/diall-app-33f6e-firebase-adminsdk-bx81a-08651ba98b.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Getting file name from request
        file = request.files['file']

        # Geting creator and description from the request
        creator = request.form['creator']
        description = request.form['description']

        # Uploading to diall-bucket
        bucket_name = 'diall-app' 
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                'ContentType': file.content_type
            }
        )

        # Storing the record in firestore
        doc_ref = db.collection('videos').document()
        doc_ref.set({
            'creator': creator,
            'description': description,
            'filename': file.filename,
            'url': f'https://{bucket_name}.s3.amazonaws.com/{file.filename}',
            'isBookmarked' : False
        })

        return 'File uploaded successfully'
    
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Video</title>
            <link rel="stylesheet" type="text/css" href="{}">
        </head>
        <body>
            <form method="post" enctype="multipart/form-data">
                <img src="static/diall.png"/>
                <h1>Diall Content Upload</h1>
                <input type="text" name="creator" placeholder="Creator Name" required>
                <input type="text" class="desc" name="description" placeholder="Description" required>
                <input type="file" name="file" required>
                <input type="submit" value="Upload">
            </form>
        </body>
        </html>
    '''.format(url_for('static', filename='style.css'))

if __name__ == '__main__':
    app.run(debug=True)
