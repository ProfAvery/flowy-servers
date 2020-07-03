#!/usr/bin/env python3

import flask
import flask_cors
import flask_redis

app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')
flask_cors.CORS(app)
redis_client = flask_redis.FlaskRedis(app)

@app.route('/set', methods=['POST'])
def post_set():
    value = flask.request.get_json()

    id = value['id']
    redis_id = f'flowy:{id}'

    redis_client.hset(redis_id, 'text',         value['text'])
    redis_client.hset(redis_id, 'checked',      int(value['checked']))
    redis_client.hset(redis_id, 'pinned',       int(value['pinned']))
    redis_client.hset(redis_id, 'collapsed',    int(value['collapsed']))

    children_id = f'{redis_id}_children'
    redis_client.delete(children_id)

    for child in value['children']:
        redis_client.rpush(children_id, child)

    return flask.jsonify({'ok': True})

@app.route('/<id>', methods=['GET'])
def get_id(id):
    redis_id = f'flowy:{id}'
    children_id = f'{redis_id}_children'

    text        = redis_client.hget(redis_id, 'text')
    checked     = redis_client.hget(redis_id, 'checked')
    pinned      = redis_client.hget(redis_id, 'pinned')
    collapsed   = redis_client.hget(redis_id, 'collapsed')
    children    = redis_client.lrange(children_id, 0, -1)

    if text is not None:
        text = text.decode('utf-8')

    response ={
        'id':           id,
        'text':         text,
        'checked':      (checked == b'1'),
        'children':     [child.decode('utf-8') for child in children],
        'pinned':       (pinned == b'1'),
        'collapsed':    (collapsed == b'1' ),
    }
    return flask.jsonify(response)

@app.route('/<id>', methods=['DELETE'])
def delete_id(id):
    redis_id = f'flowy:{id}'
    redis_client.delete(redis_id)

    return flask.jsonify({'ok': True})

