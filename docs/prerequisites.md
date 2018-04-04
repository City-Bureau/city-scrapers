---
title: Prerequisites
---

<h1 class="hidden">Prerequisites</h1>

This document covers some of the issues associated with first-time development environment setup.

## Github

### Create a Github account 
If you do not have an account already, go to [Github.com](https://github.com/) and sign up for an account.

### Installing Github
Please refer to the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) according to your operating system to install Git.

### Git 101
For a primer on Git for first-time users, see the [try.github.io](https://try.github.io/levels/1/challenges/1) or watch the [following video on how to (1) find an issue, (2) fork the code, (3) edit code, (4) open a pull request.](https://www.youtube.com/watch?list=PLyCZ96_3y5LXfPVZkHjhHRuIWhcjvCyQA&v=m_MjzgvVZ28). 

Once you have forked the code and have begun contribution, [syncing your fork](https://help.github.com/articles/syncing-a-fork/) periodically with the main City Bureau repository will be useful in staying up-to-date with the project. 

## Windows Limitations

The pty package is not available on Windows, which makes it difficult to run city scraper tests locally. We recommend that if you want to contribute more extensive code to the project, consider creating a Linux environment by installing a virtual machine, partitioning your computer or following the [Docker installation steps on the install guide](02_installation.md#step-2-option-1-local-python-3-and-virtualenv).

## Creating a virtual environment

The [following gist](https://gist.github.com/bonfirefan/c5556ca54e8bbe9d83764730c36a4b3e) covers common headaches with setting up a virtual environment on a Linux-like environment.
