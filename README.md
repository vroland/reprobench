# repobench_ng
---------

## Development Guide
----------

#### Vagrant & miniconda
After installing vagrant on your operating system, create a vagrant box and init it:
```
vagrant box add ubuntu/trusty64
vagrant init ubuntu/trusty64
```
boot your Vagrant environment:
```
vagrant up
```
then SSH into your machine:
```
vagrant ssh
```
then you download and install miniconda
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

