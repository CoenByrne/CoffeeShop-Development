import uuid
import re
from src.common.database import Database
import src.models.stores.constants as StoreConstants
import src.models.stores.errors as StoreErrors


class Store(object):
    def __init__(self, name, url_prefix, tag_name, query, _id=None):
        self.name = name
        self.url_prefix = url_prefix
        self.tag_name = tag_name
        self.query = query
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Store {}>".format(self.name)

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url_prefix": self.url_prefix,
            "tag_name": self.tag_name,
            "query": self.query
        }

    @classmethod
    def get_by_id(cls, _id):
        return cls(**Database.find_one(StoreConstants.COLLECTION, {"_id": _id}))

    def save_to_mongo(self):
        Database.update(StoreConstants.COLLECTION, {'_id':self._id}, self.json())

    @classmethod
    def get_by_name(cls, store_name):
        return cls(**Database.find_one(StoreConstants.COLLECTION, {"name": store_name}))

    @classmethod
    def get_by_url_prefix(cls, url_prefix):
        return cls(**Database.find_one(StoreConstants.COLLECTION, {"url_prefix": {"$regex": '{}'.format(url_prefix)}}))

    @classmethod
    def find_by_url(cls, url):
        """

        :param url: The item's URL
        :return: a Store or raises a StoreNotFoundException if no store matches the URL
        """

        url_regex = re.compile(r"http[s]?:\/\/(\w+\.?\w+\.\w+)|www\.(\w+\.?\w+\.\w+)")
        result = url_regex.match(url)
        if result is None:
            raise StoreErrors.StoreNotFoundException(
                "The URL Prefix used to find the store didn't give us any results!")

        if result.groups()[0] is None:
            result = result.groups()[1]
        else:
            result = result.groups()[0]

        store = cls.get_by_url_prefix(result)
        return store

    @classmethod
    def all(cls):
        return [cls(**elem) for elem in Database.find(StoreConstants.COLLECTION, {})]

    def delete(self):
        Database.remove(StoreConstants.COLLECTION, {'_id': self._id})
