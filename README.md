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
You'll need to add a 5th line with the `etp_config_id`. 

The value of the parameter is a integer you can obtain by navigating in Akamai Control Center: 

- Select Enterprise Threat Defender from the left menu
- Select Utilities 
- Select ETP Client tab 
- Locate _customer identifier_ on the right

Example of `.edgerc` file:
```
[default]
client_secret = client-secret-goes-here
host = akab-xxxx.luna.akamaiapis.net
access_token = your-access-token
client_token = your-client-token
etp_config_id = your-ETP-config-ID
```

## Updating ETP CLI module

To update to the latest version:

```
$ akamai update etp
```

## Examples

### Fetch events

Fetch the latest security events with the `event` command.
By default we fetch from 2 hours ago to 1h45 minutes ago, you can customize using start and end parameter and pass EPOCH timestamp.

```
$ akamai etp event threat
```

or Accceptable Use Policy

```
$ akamai etp event aup
```

You can pipe it to a file or your favorite JSON parser like _jq_ or _ConvertFrom-Json_ in Powershell.

```
$ akamai etp event aup --start 1576877365 --end 1576878265|jq .
```

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

One FQDN
```
$ akamai etp list add 11603 www.badguys.com
```

One IP address
```
$ akamai etp list add 11603 12.34.56.78
```

Mix of multiple items
```
$ akamai etp list add 11603 12.34.56.78 www.badguys.com
```

Load item from a file
```
$ akamai etp list add 11603 @list.txt
```

You can use pipe command
```
$ cat list.txt | akamai etp list add 11603 @-
```

Or type in and hit Ctrl+D when done
```
$ akamai etp list add 11603 @-
```

You can replace 'add' by 'remove' in the example above to remove items from list.

### Deploy changes

```
$ akamai etp list deploy 11603
```

## Troubleshooting

### ERROR: Exiting with code 404, reason: Code-130009

Make sure the API user has access to the ETP Config ID defined the .edgerc file, typically a mismatch will cause the 404 error.