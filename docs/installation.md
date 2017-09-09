# Installing the Event Aggregator

### Requirements

* Python 3
* Working internet connection

## Prerequisites

You'll need a fairly standard Python development stack. If you're on OS X, the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

## Installation

The following assumes you're using `virtualenv` and `virtualenv-wrapper`. Adjust accordingly if you aren't using these tools.

Optional but highly recommended: [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.

```bash
mkvirtualenv -p `which python3` documenters-aggregator
git clone git@github.com:City-Bureau/documenters-aggregator.git
cd documenters-aggregator
pip install -r requirements.txt
```

If using a fork, replace `City-Bureau` above with your Github username.

### If not using `virtualenv-wrapper`
`virtualenv-wrapper` gives some useful terminal commands for working with virtual environments. If you aren't using it, you just need to know which files to source for to run the commands.

Set-up:
If using a fork, replace `City-Bureau` below with your Github username.

```bash
git clone git@github.com:City-Bureau/documenters-aggregator.git
cd documenters-aggregator
virtualenv -p python3 documenters-aggregator
pip install -r requirements.txt
```

The third line above will create a folder for your virtual environment called `documenters-aggregator`. (So, there will be a parent and a child folder called `documenters-aggregator`.) The child folder has already been added to the .gitignore. To turn on the virtual environment (assuming you're in the parent `documenters-aggregator` folder):

```bash
source documenters-aggregator/bin/activate
```

To turn off the virtual environment:

```bash
deactivate
```