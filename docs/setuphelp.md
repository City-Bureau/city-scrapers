---
title: Setup Help
---

<h1 class="hidden">Setup Help</h1>

This document covers some of the issues associated with first-time development environment setup and with collaboration using Git.

## Github

### Creating a Github account 
If you do not have an account already, go to [Github.com](https://github.com/) and sign up for an account.

### Installing Github
Please refer to the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) according to your operating system to install Git.

### Git Introduction
For a primer on Git for first-time users, see the [try.github.io](https://try.github.io/levels/1/challenges/1) or watch the [following video on how to (1) find an issue, (2) fork the code, (3) edit code, (4) open a pull request.](https://www.youtube.com/watch?list=PLyCZ96_3y5LXfPVZkHjhHRuIWhcjvCyQA&v=m_MjzgvVZ28). 

### Updating your fork
Once you have forked the code and have begun contribution, [syncing your fork](https://help.github.com/articles/syncing-a-fork/) periodically with the main City Bureau repository will be useful in staying up-to-date with the project. 

1. You must first [add a remote link from which Git can track the main City Bureau project](https://help.github.com/articles/configuring-a-remote-for-a-fork/). The remote URL is <https://github.com/City-Bureau/city-scrapers.git>. Conventionally we name this remote source `upstream`. The remote source for your original cloned repository is usually named `origin`. 

```
git remote add upstream https://github.com/City-Bureau/city-scrapers.git
```
You can see your existing remotes as well by running `git remote -v`.

2. Once you've added the City Bureau remote, fetch the changes from upstream
```
git fetch upstream
```
3. Make sure you are in the branch you hope to merge changes into (typically your `master` branch), then merge the changes in. 
```
git checkout master
git merge
```
4. The final step is to update your fork on Github with the changes from the original repository by running `git push`. 

## Windows Limitations

This project uses `invoke` tasks, which rely upon the `pty` package for pseudo-terminal utilties. [Unfortunately, `pty` is not available on Windows](https://github.com/City-Bureau/city-scrapers/issues/62), which makes it difficult to run all City Scraper tests locally. We recommend that if are using Windows and  want to contribute more extensive code to the project, consider creating a Linux environment by installing a virtual machine, partitioning your computer or following the [Docker installation steps on the install guide](02_installation.md#step-2-option-1-local-python-3-and-virtualenv).

## Creating a virtual environment

The [following gist](https://gist.github.com/bonfirefan/c5556ca54e8bbe9d83764730c36a4b3e) covers common headaches with setting up a virtual environment on a Linux-like environment.
