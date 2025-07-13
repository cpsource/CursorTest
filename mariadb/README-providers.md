Excellent — you’ve provided perfect details to diagnose this.

Your MariaDB server is failing to start because of these errors:

```
[ERROR] /usr/sbin/mariadbd: unknown variable 'provider_bzip2=force_plus_permanent'
[ERROR] /usr/sbin/mariadbd: unknown variable 'provider_lz4=force_plus_permanent'
[ERROR] /usr/sbin/mariadbd: unknown variable 'provider_lzma=force_plus_permanent'
[ERROR] /usr/sbin/mariadbd: unknown variable 'provider_lzo=force_plus_permanent'
[ERROR] /usr/sbin/mariadbd: unknown variable 'provider_snappy=force_plus_permanent'
```

### Why It’s Failing

* The variables like `provider_bzip2` etc. **do not exist** in MariaDB.
* They come from **Percona Server**, which has “compression providers” for data encryption/compression plugins.
* MariaDB **does not support** these options. That’s why mariadbd refuses to start.

This means:

* Your `my.cnf` (or some included file) has these lines, probably leftover from a config designed for Percona Server or MySQL with certain compression plugins.

---

## ✅ How to Fix It

### 1. Locate the Config File Containing Those Variables

Run:

```bash
grep -R provider_bzip2 /etc/my.cnf /etc/mysql/ /etc/my.cnf.d/ /etc/mysql/conf.d/ /etc/mysql/mariadb.conf.d/ /etc/
```

Or broader:

```bash
grep -Ri provider_bzip2 /etc/
```

This will show the file containing:

```
provider_bzip2=force_plus_permanent
```

Similarly check for:

* provider\_lz4
* provider\_lzma
* provider\_lzo
* provider\_snappy

They might be in:

* **/etc/my.cnf**
* **/etc/mysql/my.cnf**
* Drop-in files in:

  * /etc/mysql/mariadb.conf.d/
  * /etc/mysql/conf.d/
  * /etc/my.cnf.d/

---

### 2. Edit the Config File

Open the file with `nano` or `vim`. Example:

```bash
sudo nano /etc/mysql/my.cnf
```

Or whatever file `grep` found.

Remove (or comment out) all lines like:

```
provider_bzip2=force_plus_permanent
provider_lz4=force_plus_permanent
provider_lzma=force_plus_permanent
provider_lzo=force_plus_permanent
provider_snappy=force_plus_permanent
```

Or comment them out:

```
# provider_bzip2=force_plus_permanent
```

---

### 3. Save the File and Restart MariaDB

After removing those variables, restart MariaDB:

```bash
sudo systemctl restart mariadb
```

Or check the status:

```bash
sudo systemctl status mariadb
```

If successful, it should show:

```
Active: active (running)
```

---

## Extra Check

If you’re unsure which config files MariaDB is reading, run:

```bash
mariadbd --help --verbose | grep -A 20 'Default options'
```

You’ll see a list like:

```
Default options are read from the following files in the given order:
/etc/my.cnf
/etc/mysql/my.cnf
...
```

This helps you know which files to examine.

---

### ⚠ Why This Happened

Someone likely copied a config from:

* Percona Server
* or MySQL with Percona plugins

…but you’re running **MariaDB**, which doesn’t recognize those options.

---

## TL;DR Fix

* Search all config files for the word `provider`
* Delete or comment out any `provider_*` lines
* Restart MariaDB

---

**Your error is purely a misconfiguration and is safe to fix as above. Once those lines are gone, MariaDB should start properly.**

Let me know if you’d like help finding the exact file or editing it!


