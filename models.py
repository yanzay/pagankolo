# coding=utf-8
from google.appengine.ext import db

class Profile(db.Model):
    user = db.UserProperty(required=True, auto_current_user_add=True)
    name = db.StringProperty(required=True)
    avatar = db.BlobProperty()
    karma = db.IntegerProperty(default=0)
    favorites = db.ListProperty(db.Key)

class Category(db.Model):
    link = db.StringProperty(required=True)
    name = db.StringProperty(required=True)

class BlogPost(db.Model):
    title = db.StringProperty(required=True)
    body = db.TextProperty(required=True)
    teaser = db.TextProperty()
    category = db.ReferenceProperty(Category, collection_name='posts')
    pub_date = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty(auto_current_user_add=True)
    author_name = db.StringProperty()
    published = db.BooleanProperty(default=True)
    rating = db.IntegerProperty()
    comments_count = db.IntegerProperty(default=0)

class Comment(db.Model):
    body = db.StringProperty(multiline=True)
    post = db.ReferenceProperty(BlogPost, collection_name='comments')
    date = db.DateTimeProperty(auto_now_add=True)
    author = db.UserProperty(auto_current_user_add=True)
    author_name = db.StringProperty()