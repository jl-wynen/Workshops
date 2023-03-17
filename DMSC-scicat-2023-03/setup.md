# Setting up

## Install requirements

**WARNING**

You should really make a new environment for this because all package versions are
pinned, and you don't want to mess up your production environment.
This hopefully avoids situations like 'Help, it doesn't work with my 2-year-old setup!'

Pick either conda or pip:

### Conda

```sh
conda env create -f scicat-workshop.yml
conda activate scicat-workshop
```

### Pip

- Make an environment with the environment-making tool of your choice (we need Python >= 3.8).
- Activate the environment.
- Then
```sh
python -m pip install -r requirements.txt
```

## SSH

Omit this step if your SSH is already set up like this.

For the time being, we have to use SSH to access the fileserver.
To make this work smoothly,

- set up an SSH-key for `login.esss.dk`
- add it to your ssh-agent (https://www.ssh.com/academy/ssh/agent)
- define an alias in `~/.ssh/config`:

```
Host login.esss.dk
    HostName login.esss.dk
    User <your-username>
    IdentityFile <private-key-file>
```

`IdentityFile` is optional in case your agent is not set up correctly.
But the rest is important.

You may choose a different host name. You'll just have to use that in the tutorial
notebook instead of the default `login.esss.dk`.
