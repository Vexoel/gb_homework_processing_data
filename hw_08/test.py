from pprint import pprint

from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
mongobase = client.instagram

profiles = mongobase['profiles']

cursor = profiles.aggregate([
    {
        '$match': {'user_name': 'tim.von.nikkel'}
    },
    {
        '$lookup': {
            'from': 'profile2follower',
            'localField': '_id',
            'foreignField': 'user_id',
            'as': 'followers'
        }
    },
    {
        '$project': {
            "followers._id": 0,
            "followers.user_id": 0
        }
    },
    {
        '$lookup': {
            'from': 'profile',
            'localField': 'followers.follower_id',
            'foreignField': '_id',
            'as': 'followers'
        }
    }
])

pprint(list(cursor))

cursor = profiles.aggregate([
    {
        '$match': {'user_name': 'vexoel'}
    },
    {
        '$lookup': {
            'from': 'profile2follower',
            'localField': '_id',
            'foreignField': 'follower_id',
            'as': 'following'
        }
    },
    {
        '$project': {
            "following._id": 0,
            "following.follower_id": 0
        }
    },
    {
        '$lookup': {
            'from': 'profile',
            'localField': 'following.user_id',
            'foreignField': '_id',
            'as': 'following'
        }
    }
])

pprint(list(cursor))
