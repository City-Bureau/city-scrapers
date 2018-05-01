This tutorial uses Codeanywhere, which runs a Virtual Private Server with its own RAM, disk space and processing power. 
We'll set up a development environment in Linux and clone the project here.

1. Get a free tier codeanywhere account at https://codeanywhere.com/signup
2. Login to Codeanywhere.
3. Start a new Container by going to File -> New Connections -> Container.
4. Choose the Blank Ubuntu 14.04 container. Name it something that makes sense to you.
5. Wait for the container to deploy, and close out of the welcome message to switch to the terminal window. (If you ever exit out of your terminal, just right click on your Container under Connections and select "SSH Terminal")
6. In order to install Python 3.6, we will have to update our directories. Run the below (line by line):

```
sudo apt-get install python-software-properties
sudo apt update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:fkrull/deadsnakes 
```
7. Now that we've added the `ppa:fkrull/deadsnakes` directory, we can install Python 3.6 and pip. Run the below:

```
sudo apt-get update
sudo apt-get install python3.6
sudo apt install python3.6-dev
sudo apt install python3.6-venv
wget https://bootstrap.pypa.io/get-pip.py
sudo python3.6 get-pip.py
sudo ln -s /usr/bin/python3.6 /usr/local/bin/python3
sudo ln -s /usr/local/bin/pip /usr/local/bin/pip3
sudo ln -s /usr/bin/python3.6 /usr/local/bin/python
```
The bottom three commands are setting your default `python` and `python3` paths. 

8. Ubuntu 14.04 comes with Python 3.4 installed out of the box, so we'll want to make sure to configure where `python3` points to:
```
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.4 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 2
sudo update-alternatives --config python3
```
You'll get the option of choose your python version. If Python 3.6 is selected, press ENTER, or type 2 to select 3.6.

9. Check that `python3` points to Python 3.6: 
```
python3 -V
```
10. One of the project dependencies is the `Inflector` python package. It will fail unless we set local encoding settings:
```
sudo apt-get install language-pack-en
export LC_ALL=en_GB.UTF-8
export LANG=en_GB.UTF-8
```
11. Now we can set up your virtualenvironment. [See these instructions for doing so.](https://gist.github.com/bonfirefan/c5556ca54e8bbe9d83764730c36a4b3e/edit)
12. Continue on with the rest of the [installation instructions](https://github.com/City-Bureau/city-scrapers/blob/master/docs/02_installation.md)
