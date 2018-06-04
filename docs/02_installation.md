---
title: Installation
---

<h1 class="hidden">Installation</h1>

Follow the following directions for cloning the repository and installing requirements.

## Prerequisites

* Git installed
* Github account
* Working internet connection
* Python installed
* Virtual environment manager

If in doubt, please also refer to the [setup help file](setuphelp.md), which should be useful for common first-time setup issues.

### Windows Limitations
This project uses `invoke` tasks, which rely upon the `pty` package for pseudo-terminal utilties. Unfortunately, `pty` is not available on Windows, which makes it difficult to run all City Scraper tests locally. We recommend that if are using Windows and want to contribute more extensive code to the project to [set up an environment on Codeanywhere](windows-remote-setup.md). This is the simplest option to start contributing code.

If you don't mind some installation and want to develop locally, you can also  consider creating a Linux environment by installing a virtual machine, partitioning your computer or [following the Docker installation steps](windows-docker-setup.md).

## Step 1: Clone the Repository

These steps are the same, regardless of which option below you choose.

1. [Fork the repository](https://github.com/City-Bureau/city-scrapers/fork) to your own Github account.

2. Clone your fork to your local machine:
```
$ git clone https://github.com/YOUR-USERNAME/city-scrapers.git
```

3. Change directories into the main project folder:
```
$ cd city-scrapers
```

*If you do not plan to do any development, you can skip creating a fork and
just clone the main City-Bureau repo.*

## Step 2: Local Python 3 and Virtualenv

You'll need a fairly standard Python development stack. If you're on OS X, the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

The following assumes you have `virtualenv` and `virtualenv-wrapper` installed.
If you are using a different virtual environment manager, please refer to its
documentation (steps 1-3 should be the same).


1. Create a virtual environment (also called city-scrapers) for the project:
```
$ mkvirtualenv -p `which python3` city-scrapers
```
The virtual environment should now be activated.

2. Install the required packages into the virtual environment:
```
(city-scrapers)$ pip install -r requirements.txt
```

You should now have a working environment for running the project or making
changes to it. Remember to always activate the virtual environment before
working with it:

```
$ workon city-scrapers
```

Should you need to deactivate the virtual environment, it is as simple as:

```
(city-scrapers)$ deactivate
```
