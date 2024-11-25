from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# API Endpoints

# 1. Create a new blog post
@app.route('/blog', methods=['POST'])
def create_blog():
    data = request.json
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    new_post = BlogPost(title=data['title'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Blog post created", "post": {"id": new_post.id, "title": new_post.title, "content": new_post.content}}), 201

# 2. Update an existing blog post
@app.route('/blog/<int:id>', methods=['PUT'])
def update_blog(id):
    data = request.json
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({"error": "Title and content are required"}), 400

    post = BlogPost.query.get(id)
    if not post:
        return jsonify({"error": "Blog post not found"}), 404

    post.title = data['title']
    post.content = data['content']
    db.session.commit()
    return jsonify({"message": "Blog post updated", "post": {"id": post.id, "title": post.title, "content": post.content}}), 200

# 3. Delete an existing blog post
@app.route('/blog/<int:id>', methods=['DELETE'])
def delete_blog(id):
    post = BlogPost.query.get(id)
    if not post:
        return jsonify({"error": "Blog post not found"}), 404

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Blog post deleted"}), 204

# 4. Get a single blog post
@app.route('/blog/<int:id>', methods=['GET'])
def get_blog(id):
    post = BlogPost.query.get(id)
    if not post:
        return jsonify({"error": "Blog post not found"}), 404

    return jsonify({"post": {"id": post.id, "title": post.title, "content": post.content}}), 200

# 5. Get all blog posts
@app.route('/blog', methods=['GET'])
def get_all_blogs():
    posts = BlogPost.query.all()
    return jsonify({
        "posts": [{"id": post.id, "title": post.title, "content": post.content} for post in posts]
    }), 200

# 6. Filter blog posts by a search term
@app.route('/blog/search', methods=['GET'])
def search_blog():
    term = request.args.get('q')
    if not term:
        return jsonify({"error": "Search term is required"}), 400

    posts = BlogPost.query.filter(
        BlogPost.title.contains(term) | BlogPost.content.contains(term)
    ).all()

    if not posts:
        return jsonify({"message": "No blog posts found"}), 404

    return jsonify({
        "posts": [{"id": post.id, "title": post.title, "content": post.content} for post in posts]
    }), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
