---
title: Installation
---

<h1 class="hidden">Installation</h1>

Follow the following directions if you'd like to run the project on your
machine.

## Prerequisites

* Github account
* Working internet connection

## Step 1: Clone the Repository

These steps are the same, regardless of which option below you choose.

1. [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.

2. Clone your fork to your local machine:
```
$ git clone git@github.com:<your-username>/documenters-aggregator.git
```

3. Change directories into the main project folder:
```
$ cd documenters-aggregator
```

*If you do not plan to do any development, you can skip creating a fork and
just clone the main City-Bureau repo.*

## Step 2, Option 1: Local Python 3 and Virtualenv

You'll need a fairly standard Python development stack. If you're on OS X, the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

The following assumes you have `virtualenv` and `virtualenv-wrapper` installed.
If you are using a different virtual environment manager, please refer to its
documentation (steps 1-3 should be the same).


1. Create a virtual environment (also called documenters-aggregator) for the project:
```
$ mkvirtualenv -p `which python3` documenters-aggregator
```
The virtual environment should now be activated.

2. Install the required packages into the virtual environment:
```
(documenters-aggregator)$ pip install -r requirements.txt
```

You should now have a working environment for running the project or making
changes to it. Remember to always activate the virtual environment before
working with it:

```
$ workon documenters-aggregator
```

Should you need to deactivate the virtual environment, it is as simple as:

```
(documenters-aggregator)$ deactivate
```


### Step 2, Option 2: Docker

This is a good option for Windows or a system that doesn't have any of the above prerequisites installed but does have Docker. You will first have to install Docker [here](https://docs.docker.com/install/). Older Mac and Windows systems may need to use [Docker Toolbox](https://docs.docker.com/toolbox/overview/) instead.

1. [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.

2. Clone your fork to your local machine:
```
$ git clone git@github.com:<your-username>/documenters-aggregator.git
```

3. Change directories into the main project folder:
```
$ cd documenters-aggregator
```

4. Build the docker container. Don't forget final ".", which tells Docker to use the Dockerfile in the current directory. The "-t" flag adds a tag to the image so that it gets a nice repository name and tag. This tag matches the [Docker Hub docker repository](https://hub.docker.com/r/easherma/documenters-aggregator), but you can add other tags. For more information, read the [Docker docs.](https://docs.docker.com/)
```
$ docker build -t easherma/documenters-aggregator .
```

Then you can run commands on the container. For instance, to run tests:

```
$ docker run easherma/documenters-aggregator invoke runtests
```
