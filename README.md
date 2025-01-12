# uva-luyanfei

[![PyPI - Version](https://img.shields.io/pypi/v/uva-luyanfei.svg)](https://pypi.org/project/uva-luyanfei)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/uva-luyanfei.svg)](https://pypi.org/project/uva-luyanfei)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install uva-luyanfei
```

## Usage
Python urllib does not work for onlinejudge.org, so this tool use curl to post and get. You need to install curl first. 
This also means this tool will not work for Windows.

### Login
```console
uva login -u xxx -p xxx
```

### Download pdf
```console
uva download -p (problem id)
```

### Show submissions
```console
uva status
```

### Submit problem solution
```console
uva submit -p (problem id) -f (source file) -l (language, default to 'C++11')
```

## License

`uva-luyanfei` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
