import boto3
import requests
from os import environ, remove
import piexif
import time
from urllib.parse import urlparse

BUCKET="i.ruqqus.com"

#setup AWS connection
S3=boto3.client("s3",
                aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY")
                )

def upload_from_url(name, url):

    print('upload from url')
    
    x=requests.get(url)

    print('got content')

    tempname=name.replace("/","_")

    with open(tempname, "wb") as file:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            
    if tempname.split('.')[-1] in ['jpg','jpeg']:
        piexif.remove(tempname)
    
    S3.upload_file(tempname,
                      Bucket=BUCKET,
                      Key=name,
                      ExtraArgs={'ACL':'public-read',
                                 "ContentType":"image/png"
                      }
                     )

    remove(tempname)
    

def upload_file(name, file):

    #temp save for exif stripping
    tempname=name.replace("/","_")

    file.save(tempname)
    
    if tempname.split('.')[-1] in ['jpg','jpeg']:
        piexif.remove(tempname)
    
    S3.upload_file(tempname,
                      Bucket=BUCKET,
                      Key=name,
                      ExtraArgs={'ACL':'public-read',
                                 "ContentType":"image/png"
                      }
                     )

    remove(tempname)

def upload_from_file(name, filename):

    tempname=name.replace("/","_")

    if filename.split('.')[-1] in ['jpg','jpeg']:
        piexif.remove(tempname)
    
    S3.upload_file(tempname,
                      Bucket=BUCKET,
                      Key=name,
                      ExtraArgs={'ACL':'public-read',
                                 "ContentType":"image/png"
                      }
                     )

    remove(filename)

def delete_file(name):

    S3.delete_object(Bucket=BUCKET,
                     Key=name)

def check_csam(post):
    
    #Relies on Cloudflare's photodna implementation
    #451 returned by CF = positive match

    #ignore non-link posts
    if not post.url:
        return

    parsed_url=urlparse(post.url)

    if parsed_url.netloc != BUCKET:
        return

    headers={"User-Agent":"Ruqqus webserver"}
    for i in range(10):
        x=requests.get(post.url, headers=headers)

        if x.status_code in [200, 451]:
            break
        else:
            time.sleep(20)

    if x.status_code==200:
        return

    #ban user and alts
    post.author.is_banned=1
    db.add(v)
    for alt in post.author.alts:
        alt.is_banned=1
        db.add(alt)

    #remove content
    post.is_banned=True
    db.add(post)

    #nuke aws
    delete_file(parsed_url.path.lstrip('/'))
    
    
    db.commit()

    
    

    
