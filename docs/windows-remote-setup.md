# Developing on Codeanywhere
This tutorial uses Codeanywhere as an alternative to developing on Windows. Codeanywhere runs a Virtual Private Server with its own RAM, disk space and processing power. 
We'll set up a Linux development environment in a Codeanywhere container to clone the project in.

## Steps:
1. Codeanywhere setup
2. Environment setup and installation
3. Next steps

## 1. Codeanywhere setup
1. Get a free tier codeanywhere account at https://codeanywhere.com/signup
2. Login to Codeanywhere.
3. Start a new Container by going to File -> New Connections -> Container.
4. Choose the **Blank: Ubuntu 14.04** container. Name it something that makes sense to you.
5. Wait for the container to deploy, and close out of the welcome message to switch to the terminal window. (If you ever exit out of your terminal, just right click on your Container under Connections and select "SSH Terminal")

## 2. Environment setup and installations
### Option 1: Run a shell script to set everything up:
This command runs all of the setup commands at once. Copy and right click to paste into your terminal.
```
source <(curl -s https://gist.githubusercontent.com/pjsier/06c03529c8cde7255f2ea0c3dd2d7e7c/raw/9784f283f32073d5e2a83f90b31d70f8b9e0111b/city_scrapers_setup.sh)
```

### Option 2: Run the commands step-by-step (in case the shell script did not work, or you want more explanations)
1. In order to install Python 3.6, we will have to update our directories. Run the below (line by line):

```
sudo apt update -y
sudo apt-get install -y python-software-properties
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:fkrull/deadsnakes -y
```

2. Now that we've added the `ppa:fkrull/deadsnakes` directory, we can install Python 3.6 and pip. Run the below:

```
sudo apt-get update -y
sudo apt-get install python3.6
sudo apt install -y python3.6-dev
sudo apt install -y python3.6-venv

wget https://bootstrap.pypa.io/get-pip.py
sudo python3.6 get-pip.py
rm get-pip.py
```

3. One of the project dependencies is the `Inflector` python package. It will fail unless we set local encoding settings:

```
sudo apt-get install -y language-pack-en
echo "export LC_ALL=en_GB.UTF-8" >> ~/.bashrc
echo "export LANG=en_GB.UTF-8" >> ~/.bashrc
source ~/.bashrc
```

## 3. Next Steps: 

1. Create your virtual environment: 

```
python3.6 -m venv cityscraperenv
source cityscraperenv/bin/activate
```
Note: these steps differ from those in the [installation instructions](https://github.com/City-Bureau/city-scrapers/blob/master/docs/02_installation.md). The only difference is that you are using `venv` to set up your virtual environment and specifying which Python 3 version you are using (3.6).

Once you've activated your virtual environment, you should see it appear in parenthesis: 

```
(cityscraperenv)$
```
To deactivate, type `deactivate`. To activate it, re-run the `source cityscraperenv/bin/activate` command. You'll want to activate the virtual environment when developing for the City Scrapers project.

2. Continue on with the rest of the [installation instructions](https://github.com/City-Bureau/city-scrapers/blob/master/docs/02_installation.md). You will need to clone your repository and install the requirements in your virtual environment. 
