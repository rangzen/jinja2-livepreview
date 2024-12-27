# Jinja2 Live Preview

Fork of Jinja2 Live Preview with HTML and no Ansible.

## Running the project

### Via Docker

    docker run --rm -p 9797:9797 rangzen/jinja2-livepreview

If you want to change the port, specify the `PORT` environment variable like:

    docker run --rm -e PORT=5000 -p 5000:5000 rangzen/jinja2-livepreview

## Dev Installation

- `npm install -g nodemon`.
- `poetry install`.
- Set the Python Interpreter in VScode if needed.
- `poetry shell`.
- `make docker/assets`.
- `make dev`
- Open `http://localhost:9797`.

## References

- <https://github.com/crccheck/jinja2-livepreview> Original by `crccheck`.
- <https://github.com/abourguignon/jinja2-live-parser> Original by `abourguignon`.
