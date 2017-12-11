# Installing the Event Aggregator

## Requirements

* Github account
* Python 3
* Working internet connection

You'll need a fairly standard Python development stack. If you're on OS X, the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).


## Installation

The following assumes you have `virtualenv` and `virtualenv-wrapper` installed.

1. [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.
2. Clone your fork to your local machine:
``` $ git clone git@github.com:<your-username>/documenters-aggregator.git ```
3. Change directories into the main project folder:
``` $ cd documenters-aggregator ```
4. Create a virtual environment (also called documenters-aggregator) for the project:
``` $ mkvirtualenv -p `which python3` documenters-aggregator ```
The virtual environment should now be activated.
5. Install the required packages into the virtual environment:
``` (documenters-aggregator)$ pip install -r requirements.txt ```

To activate the virtual environment:
``` $ workon documenters-aggregator ```

To deactivate the virtual environment:
``` (documenters-aggregator)$ deactivate ```


## Alternative Installation: Docker

Good option for Windows. If you have Docker installed on your machine, the process becomes pretty simple.

1. [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.
2. Clone your fork to your local machine:
``` $ git clone git@github.com:<your-username>/documenters-aggregator.git ```
3. Change directories into the main project folder:
``` $ cd documenters-aggregator ```
4. Build the docker container:
``` $ docker build -t easherma/documenters-aggregator . ```

Then you can run commands on the container. For instance, to run tests:

``` 
$ docker run easherma/documenters-aggregator invoke runtests
```
