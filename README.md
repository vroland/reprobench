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
then you download and install miniconda:
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

After this clone this repository to your machine:
```
git clone -b jkf_wip https://github.com/daajoe/reprobench.git
```

then move to thir directory:
```
cd reprobench
```

Now we will create an environment based on the yaml file there:
```
conda env create -f environment.yml
```

then activate that environment:
```
conda activate rb
```

Verify that the new environment was installed correctly:
```
conda env list
```
You can also use `conda info --envs`
