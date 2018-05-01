# Developing using Docker 

It's recommended that you try [setting up an environment on Codeanywhere](windows-remote-setup.md) if you are trying to develop on Windows. 
If you would still like to develope locally, this is a good option for Windows or a system that doesn't have any of the above prerequisites installed but does have Docker. You will first have to install Docker [here](https://docs.docker.com/install/). Older Mac and Windows systems may need to use [Docker Toolbox](https://docs.docker.com/toolbox/overview/) instead.

1. [Fork the repository](https://github.com/City-Bureau/city-scrapers/fork) to your own Github account.

2. Clone your fork to your local machine:
```
$ git clone git@github.com:<your-username>/city-scrapers.git
```

3. Change directories into the main project folder:
```
$ cd city-scrapers
```

4. Build the docker container. Don't forget final ".", which tells Docker to use the Dockerfile in the current directory. The "-t" flag adds a tag to the image so that it gets a nice repository name and tag. This tag matches the [Docker Hub docker repository](https://hub.docker.com/r/easherma/documenters-aggregator), but you can add other tags. For more information, read the [Docker docs.](https://docs.docker.com/)
```
$ docker build -t easherma/documenters-aggregator .
```

Then you can run commands on the container. For instance, to run tests:

```
$ docker run easherma/documenters-aggregator invoke runtests
```
