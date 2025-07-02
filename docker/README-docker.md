Excellent — let’s clarify exactly what’s happening under the hood.

When you run:

```bash
docker run hello-world
```

…and see:

```
The Docker client contacted the Docker daemon.
```

…it’s referring to the **communication between the Docker client (the CLI tool) and the Docker daemon (dockerd).**

---

## ✅ What “port” does that communication use?

**Short answer:**

* **By default, no TCP port at all.**
* The Docker client and daemon communicate via a **Unix socket**:

  ```
  /var/run/docker.sock
  ```

So there’s **no TCP port involved on localhost** unless you explicitly configure one.

---

## ✅ Default: Unix Socket

On Linux systems (like your Ubuntu 24.04), the default Docker daemon startup uses:

```
Host: unix:///var/run/docker.sock
```

Meaning:

* The client sends commands to the daemon by writing to that Unix socket file.
* No network port is listening.
* It’s purely a local file-based IPC (inter-process communication).

You can confirm this:

```bash
ps aux | grep dockerd
```

You’ll see something like:

```
dockerd -H unix:///var/run/docker.sock
```

---

## ✅ Optional: TCP Socket

If you want Docker to listen on a network port, you’d start dockerd like:

```
dockerd -H tcp://0.0.0.0:2375
```

So:

* The Docker daemon listens on **TCP port 2375** (insecure) or **2376** (TLS).
* Clients connect to that port.

This is used when:

* Running Docker remotely
* Managing Docker on other machines

But **it’s OFF by default** because it can expose your Docker daemon to remote attacks.

---

## ✅ How to Check Where Docker is Listening

Run:

```bash
docker info | grep -i socket
```

Example:

```
Docker Root Dir: /var/lib/docker
Docker Socket: unix:///var/run/docker.sock
```

Or check dockerd’s process:

```bash
ps aux | grep dockerd
```

---

## ✅ On Windows / macOS

On Docker Desktop, the Docker client also uses:

* A named pipe (Windows) like:

  ```
  //./pipe/docker_engine
  ```
* A Unix domain socket on macOS

---

## ✅ How to Enable Docker on a TCP Port

**⚠️ Warning:** Exposing Docker via TCP without TLS is dangerous.

To enable:

```bash
sudo dockerd -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375
```

Or edit:

```
/etc/docker/daemon.json
```

Example:

```json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
}
```

Then restart Docker:

```bash
sudo systemctl restart docker
```

---

## ✅ TL;DR

✅ By default:
→ Docker CLI ↔ Docker daemon uses:

```
/var/run/docker.sock
```

→ **No TCP port** involved

✅ Only uses a TCP port if you explicitly enable it:

* TCP 2375 → insecure
* TCP 2376 → secure (TLS)

---

**Bottom line:**

> The message **“The Docker client contacted the Docker daemon.”** means:
>
> * On Linux → it talked to the daemon over the Unix socket
> * No network port used unless configured

Let me know if you’d like to:

* Expose Docker over TCP
* Check your Docker daemon’s exact config
* Or run Docker remotely!


