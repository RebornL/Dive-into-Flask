from flask import Flask, render_template
from config import DevConfig
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import func
from wtforms import StringField, TextAreaField
from flask_wtf import Form
from wtforms.validators import DataRequired, Length
import datetime

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
#track_modifications = app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', True)
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

tags = db.Table('post_tags',
    db.Column('post_id', db.Integer(), db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id'))
)

#the type of data
class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    posts = db.relationship(#在SQLAlchemy中创建一个虚拟的列
        'Post',#建立关联的数据对象
        backref='user',
        lazy='dynamic'#加载查询方式
    )

    def __init__(self,username):
        self.username = username;
        self.password = '';
    def __repr__(self):
        return "<User '{}'>".format(self.username)

#建立一个数据模型之间的关联----一对多
class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))#外键约束,user.id直接采用表名
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
    )
    tags = db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
    )

    def __init__(self, title):
        self.title = title
    
    def __repr__(self):
        return "<Post '{}'>".format(self.title)

#创建一个数据类型实现用户评论
class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    idpost_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])

#多对多
class Tag(db.Model):
    id = db.Column(db.Integer(),primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self,title):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title) 

#评论表单
class CommentForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'Comment', validators=[DataRequired()])

#侧边栏信息
def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
        ).join(
            tags
            ).group_by(Tag).order_by('total DESC').limit(5).all()

    return recent, top_tags

@app.route('/')
@app.route('/<int:page>')
def home(page=1):
    # return '<h1>Hello World!</h1>'
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page, 10)
    recent, top_tags = sidebar_data()

    return render_template('home.html',posts=posts, recent=recent, top_tags=top_tags)

@app.route('/post/<int:post_id>',methods=('GET', 'POST'))
def post(post_id):
    post = Post.query.get_or_404(post_id)#根据post_id获取post
    tags = post.tags#通过tags获取标签
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent,top_tags = sidebar_data()
    #新建一个评论框
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.datetime.now()
        db.session.add(new_comment)
        db.session.commit()

    return render_template('post.html',post=post, tags=tags, comments=comments, recent=recent, top_tags=top_tags,form=form)

@app.route('/tag/<string:tag_name>')
def tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags = sidebar_data()

    return render_template('tag.html',tag=tag, posts=posts, recent=recent, top_tags=top_tags)

@app.route('/user/<string:username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags = sidebar_data()

    return render_template('user.html', user=user, posts=posts, recent=recent, top_tags=top_tags)


if __name__ == '__main__':
    app.run()