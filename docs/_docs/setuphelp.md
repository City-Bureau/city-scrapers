---
title: "Setup Help"
permalink: /docs/setup-help/
excerpt: "Intro to City Scrapers"
last_modified_at: 2018-10-04T20:15:56-04:00
toc: false
---

This document covers some of the issues associated with first-time development environment setup and with collaboration using Git.

## Git and GitHub

### Installing Git

Please refer to the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git){:target="\_blank"} according to your operating system to install Git.

### Git 101

For a primer on Git for first-time users, see the [try.github.io](https://try.github.io/levels/1/challenges/1){:target="\_blank"} or watch the [following video](https://www.youtube.com/watch?list=PLyCZ96_3y5LXfPVZkHjhHRuIWhcjvCyQA&v=m_MjzgvVZ28){:target="\_blank"} on how to (1) find an issue, (2) fork the code, (3) edit code, (4) open a pull request.

Once you have forked the code and have begun contribution, [syncing your fork](https://help.github.com/articles/syncing-a-fork/){:target="\_blank"} periodically with the main City Bureau repository will be useful in staying up-to-date with the project.

\1. You must first [add a remote link](https://help.github.com/articles/configuring-a-remote-for-a-fork/){:target="\_blank"} from which Git can track the main City Bureau project. The remote URL is `<https://github.com/City-Bureau/city-scrapers.git>`. Conventionally we name this remote source `upstream`. The remote source for your original cloned repository is usually named `origin`.

```shell
$ git remote add upstream https://github.com/City-Bureau/city-scrapers.git
```

You can see your existing remotes as well by running `git remote -v`.

\2. Once you've added the City Bureau remote, fetch the changes from upstream

```shell
$ git fetch upstream
```

\3. Make sure you are in the branch you hope to merge changes into (typically your `master` branch), then merge the changes in from the `upstream/master` branch.

```shell
$ git checkout master
$ git merge upstream/master
```

\4. The final step is to update your fork on Github with the changes from the original repository by running `git push`.

### Creating a GitHub account

If you do not have an account already, go to [GitHub](https://github.com){:target="\_blank"} and sign up for an account.

## Python and Pipenv

### Installing Python

Here are some helpful links for setting up Python on your computer:

- [Codecademy: Set-up Python](https://www.codecademy.com/articles/setup-python)
- [Get started using Python on Windows for beginners](https://docs.microsoft.com/en-us/windows/python/beginners){:target="\_blank"}

### Installing and using Pipenv

[Pipenv](https://pipenv.readthedocs.io/en/latest/) is package management tool for Python which combines managing dependencies and virtual environments. It's also designed to be compatible with Windows. Other tools like `virtualenv` and `virtualenv-wrapper` can be used, but our documentation will only refer to Pipenv since it's quickly being adopted as the standard for Python dependency management.

You can see installation instructions for Pipenv in the [Installing Pipenv](https://pipenv.kennethreitz.org/en/latest/install/#installing-pipenv) section of the documentation.

### Configuring your code editor

Most text editors can be configured to fix code style issues for you based off of the configuration settings in `setup.cfg`. Here's an example for VSCode using the [standard Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python){:target="\_blank"} (which can be modified/added at `.vscode/settings.json` in your project directory):

```json
{
  "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.envFile": "${workspaceRoot}/.env",
  "python.linting.flake8Args": ["--config", "${workspaceRoot}/setup.cfg"],
  "python.formatting.provider": "yapf",
  "python.formatting.yapfArgs": ["--style", "${workspaceRoot}/setup.cfg"],
  "python.sortImports.path": "${workspaceRoot}/.venv/bin/isort",
  "python.sortImports.args": [
    "--settings-path=${workspaceFolder}/setup.cfg"
  ],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "editor.formatOnSave": true,
  "editor.rulers": [100]
}
```

This configuration will run linting and style checks for you, and also make necessary changes automatically any time you save. Packages are available for [Atom](https://atom.io/packages/linter-flake8){:target="\_blank"} and [Sublime Text](https://fosstack.com/setup-sublime-python/){:target="\_blank"} as well.
