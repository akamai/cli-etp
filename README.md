# Akamai CLI: Enterprise Threat Protector

## Scope

Enterprise Threat Protector (ETP) comes with a full suite of APIs. 
Yet you need to build scripts to be able to interact with the service.

That's where Akamai CLI toolkit greatly help, no longer script to wrote yourself, you can run very common operations directly from the command line.

The kit also takes care of all the dependencies like Python version or modules.

## Prerequisites

### Akamai CLI

You'll need the CLI toolkit, available on many platform.
Please visit the [Getting Started](https://developer.akamai.com/cli/docs/getting-started) guide on developer.akamai.com.

## Install

Installation is done via `akamai install`:

```
$ akamai install etp
```

Running this will run the system `python setup.py` automatically. 

### API User and configuration file

On Akamai Control Center, make sure you create an API user with the _ETP Configuration API_ (`/etp-config`) with read-write permission.

Upon user credential creation, you'll get a `.edgerc` file with 4 parameters.
You'll need to add a 5th line with the etp_config_id you can get going into the Enterprise Threat Defender > Utilities

Example of `.edgerc` file:
```
[default]
client_secret = client-secret-goes-here
host = akab-xxxx.luna.akamaiapis.net
access_token = your-access-token
client_token = your-client-token
etp_config_id = your-ETP-config-ID
```

## Updating

To update to the latest version:

```
$ akamai update etp
```

## Example

Get the lists available on the account
```
$ akamai etp list get
```

The result is a coma separated lines:

```
7721,Custom Blacklist
11981,LOLCats Blacklist
11603,Zero Trust Demo Blacklist
11821,Zero Trust Demo Whitelist
14461,Social Media
14821,White List Domains
13641,Serial sequence testing
```

### Add items to a list

FQDN
```
$ akamai etp list add 11603 www.badguys.com
```

IP address
```
$ akamai etp list add 11603 12.34.56.78
```

### Deploy changes

```
$ akamai etp list deploy 11603
```

