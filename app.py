import os
import re

from flask import Flask, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


@app.route("/perform_query", methods=["POST"])
def perform_query():
    req = request.values.to_dict()

    if not {'file_name', 'cmd1', 'value1', 'cmd2', 'value2'} <= req.keys():
        return '', 400

    file_name = req['file_name']
    del req['file_name']

    if file_name not in list(os.walk(DATA_DIR))[-1][-1]:
        return '', 400

    cmd_1 = req.get('cmd1')
    value_1 = req.get('value1')
    cmd_2 = req.get('cmd2')
    value_2 = req.get('value2')

    if not all(x in ['map', 'filter', 'unique', 'sort'] for x in [cmd_1, cmd_2]):
        return '', 400

    path = os.path.join(DATA_DIR, file_name)

    with open(path, 'r') as f:
        gen = (raw for raw in f)
        gen = file_processing(cmd_1, value_1, gen)
        gen = file_processing(cmd_2, value_2, gen)
        result = "\n".join(list(gen))

    return app.response_class(result, content_type="text/plain")


def file_processing(cmd, value, gen):
    if cmd == 'filter':
        return filter(lambda raw: value in raw, gen)
    elif cmd == 'map':
        return map(lambda x: re.split(' - - | "|" ', x)[int(value)].rstrip(), gen)
    elif cmd == 'unique':
        return set(gen)
    elif cmd == 'sort':
        return sorted(gen, reverse=True if value.lower() == 'asc' else False)


if __name__ == "__main__":
    app.run(debug=True)
