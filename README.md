# planetai-chainseg

description

## Installation
For unix:
```sh
poetry install
```

For macOS:
You might need to change the `tensorflow` entry in the `pyproject.toml` to 
```
tensorflow-macos = {version = "^2.14.0", optional = true}
```
Then run `poetry install`.

## Run

### From commandline

Run the following command for starting the program with application 
of a neural model and UDP as source 
```sh
rov-assist 
```

Run for info on the modes:
```sh
rov-assist --help
```

### From script
See the `examples` folder for scripts.


