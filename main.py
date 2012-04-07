# coding=utf-8
import os
from google.appengine.api import users, images
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from models import BlogPost, Profile, Category, Comment

template_dir = os.path.dirname(__file__)+'/templates'

class BaseHandler(webapp.RequestHandler):
    def __init__(self,*args,**kwargs):
        super(BaseHandler,self).__init__(*args,**kwargs)
        user = users.get_current_user()
        user_name, prof_id = self.getUserNameAndID(user)
        self.templ_vals = {
            'user':user,
            'login_url':users.create_login_url(self.request.url),
            'logout_url':users.create_logout_url(self.request.url),
            'user_name':user_name,
            'prof_id':prof_id
        }

    def render_to_response(self,tmpl_name,tmpl_vals={}):
        path = os.path.join(template_dir,tmpl_name)
        self.response.out.write(template.render(path,tmpl_vals))

    def getUserNameAndID(self,user):
        prof = Profile.all().filter('user = ', user).get()
        if prof:
            return prof.name, prof.key()
        return None, None

    def getCurrentUserName(self):
        user = users.get_current_user()
        prof = Profile.all().filter('user = ', user).get()
        if prof:
            return prof.name
        return None

    def getProfile(self, user):
        return Profile.all().filter('user = ', user).get()

class MainHandler(BaseHandler):
    def get(self,page):
        if page:
            page = int(page)
            offset = (page-1)*10
        else:
            offset = 0
            page = 1
        num_pages, ost = divmod(BlogPost.all().count(),10)
        if ost>0:
            num_pages += 1
        posts = BlogPost.all().order('-pub_date').fetch(limit=10,offset=offset)
        self.templ_vals.update({
            'url':users.create_logout_url("/"),
            'posts':posts,
            'active_main':True,
            'page':page,
            'pages':range(1,num_pages+1)
        })
        self.render_to_response('index.html',self.templ_vals)

class BlogsHandler(BaseHandler):
    def get(self):
        self.templ_vals.update({
            'blogs': Category.all().order('name'),
            'active_blogs':True
        })
        self.render_to_response('blog_list.html',self.templ_vals)

class AddPostHandler(BaseHandler):
    @login_required
    def get(self):
        user = users.get_current_user()
        prof = db.GqlQuery('SELECT * FROM Profile WHERE user = :1', user).get()
        if not prof:
            unnamed = True
        else:
            unnamed = False
        categories = Category.all()
        self.templ_vals.update({
            'url': users.create_logout_url("/"),
            'unnamed':unnamed,
            'categories':categories
        })
        self.render_to_response('add_form.html', self.templ_vals)

    def post(self):
        name = self.request.get('name')
        user = users.get_current_user()
        if name:
            prof = Profile(
                name=name,
                user=user
            )
            prof.put()
        category_link = self.request.get('category')
        category = Category.all().filter('link = ', category_link).get()
        p = BlogPost(
            title=self.request.get('title'),
            body=self.request.get('body'),
            category=category
        )
        p.teaser = self.makeTeaser(p.body)
        user_name, prof_id = self.getUserNameAndID(user)
        p.author_name = user_name
        p.put()
        self.redirect('/')

    def makeTeaser(self, body):
        pos = body.find('<!-- teaser brake -->')
        if pos > -1:
            return body[:pos]
        else:
            return body


class AddCommentHandler(BaseHandler):
    def post(self):
        post = BlogPost.get_by_id(int(self.request.get('postid')))
        c = Comment(
            body = self.request.get('body'),
            post = post,
            author_name = self.getCurrentUserName()
        )
        c.put()
        post.comments_count += 1
        post.put()
        templ_vals = {
            'comment': c
        }
        self.render_to_response('comment.html',templ_vals)
#        self.redirect('/blogs/%s/%s' % (post.category.link, post.key().id()))

class EditProfileHandler(BaseHandler):
    def get(self):
        prof = Profile.all().filter('user = ',users.get_current_user()).get()
        self.templ_vals.update({
            'profile':prof
        })
        self.render_to_response('edit_profile.html',self.templ_vals)

    def post(self, *args):
        name = self.request.get('name')
        prof = Profile.all().filter('user = ',users.get_current_user()).get()
        if not prof:
            prof = Profile(name=name)
        else:
            prof.name = name
        avatar = self.request.get('avatar')
        avatar = images.resize(avatar,32,32)
        prof.avatar = db.Blob(avatar)
        prof.put()
        self.redirect('/')

class Avatar(webapp.RequestHandler):
    def get(self, *args):
        prof = db.get(self.request.get('img_id'))
        if prof.avatar:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(prof.avatar)
        else:
            self.error(404)

class SingleBlogHandler(BaseHandler):
    def get(self,name):
        cat = Category.all().filter('link = ',name).get()
        posts = BlogPost.all().filter('category = ',cat.key()).order('-pub_date')
        templ_val = {
            'posts': posts,
            'active_blogs':True
        }
        self.render_to_response('index.html',templ_val)

class PostHandler(BaseHandler):
    def get(self,blog,id):
        post = BlogPost.get_by_id(int(id))
        templ_val = {
            'post': post,
            'active_blogs':True,
            'comments':post.comments.order('date')
        }
        self.render_to_response('post.html',templ_val)

class AddCategoryHandler(BaseHandler):
    def get(self):
        self.render_to_response('add_category.html')

    def post(self, *args):
        c = Category(
            name=self.request.get('name'),
            link=self.request.get('link')
        )
        c.put()
        self.redirect('/admin')

app = webapp.WSGIApplication(
    [('/()', MainHandler),
    ('/page([0-9])*', MainHandler),
    ('/add', AddPostHandler),
    ('/add_comment', AddCommentHandler),
    ('/admin',AddCategoryHandler),
    ('/blogs/{0,1}',BlogsHandler),
    ('/blogs/([a-z]*)/{0,1}',SingleBlogHandler),
    ('/blogs/([a-z]*)/([0-9]*)/{0,1}',PostHandler),
    ('/profile/edit',EditProfileHandler),
    ('/img',Avatar)],
    debug=True
)