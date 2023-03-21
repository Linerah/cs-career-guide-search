import hashlib
import json
import time

from flask import jsonify


def generate_blog_id():
    """ Generates a unique blog's id
    """
    cur_time = str(time.time())
    hashed_time = hashlib.sha1()
    hashed_time.update(cur_time.encode("utf8"))
    return hashed_time.hexdigest()


class Blog:

    def __init__(self, tittle, information, link, user_id):
        self.blog_id = generate_blog_id()
        self.tittle = tittle
        self.information = information
        self.link = link
        self.date_published = time.time()
        self.upvote_count = 0
        self.read_count = 0
        self.user_id = user_id

    @staticmethod
    def create_blog(tittle, information, link, user_id, database):
        """ A static method, that creates a blog object and adds it to the database
        """
        blog = Blog(tittle, information, link, user_id)
        blog_document = blog.to_json()
        collection = database.db.blogs
        print(blog_document)
        collection.insert_one(blog_document)
        return blog

    @staticmethod
    def get_blogs(database):
        """ A static method, that gets all of the blogs in the database
        """
        collection = database.db.blogs  # TODO: try to see if Atlas search has an AI that orders by relevance
        blogs = collection.find()
        return list(blogs)

    @staticmethod
    def get_filtered_blogs(database, blog_filter, blog_tittle):
        """ A static method, that filters blogs by the given input from the user
        """

        collection = database.db.blogs
        query = {'query': blog_tittle, 'path': 'blog_tittle'}
        pipeline = [
            {
                '$search': {
                    'index': 'tittleSearchIndex',  # TODO: create search index in Atlas Search
                    'text': query
                }
            }
        ]
        if not blog_filter and not blog_tittle:
            return collection.find()
        elif not blog_filter:
            return collection.aggregate(pipeline)
        elif not blog_tittle:
            if blog_filter == "Newest":
                return collection.find().sort("date_published", -1)
            elif blog_filter == "Most read":
                return collection.find().sort("read_count", -1)
            elif blog_filter == "Most upvote":
                return collection.find().sort("upvote_count", -1)

            # this returns the blogs ordered "Oldest"
            return collection.find().sort("date_published", 1)

        if blog_filter == "Newest":
            sort_criteria = {"date_published", -1}
            pipeline.append({"$sort": sort_criteria})
            return collection.aggregate(pipeline)
        elif blog_filter == "Most read":
            sort_criteria = {"read_count", -1}
            pipeline.append({"$sort": sort_criteria})
            return collection.aggregate(pipeline)
        elif blog_filter == "Most upvote":
            sort_criteria = {"upvote_count", -1}
            pipeline.append({"$sort": sort_criteria})
            return collection.aggregate(pipeline)

        sort_criteria = {"date_published", 1}
        pipeline.append({"$sort": sort_criteria})
        return collection.aggregate(pipeline)

    def to_json(self):
        """ Converts a blog object to json format
        """
        return {'blog_id': self.blog_id, 'tittle': self.tittle, 'information': self.information, 'link': self.link,
                'date_published': self.date_published, 'upvote_count': self.upvote_count, 'read_count': self.read_count,
                'user_id': self.user_id}