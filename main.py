from flask import Flask, render_template
from config import DevConfig
from flask.ext.sqlalchemy import SQLAlchemy, func

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

//侧边栏信息
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

if __name__ == '__main__':
    app.run()