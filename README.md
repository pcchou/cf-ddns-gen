cf-ddns-gen
===========

A python script, made to simplify the process of generating a CloudFlare DDNS update script.<br>
By pcchou, Released under [the MIT License](https://github.com/pcchou/cf-ddns-gen/LICENSE).

Inspired by [larrybolt](https://github.com/larrybolt)'s [original DDNS script](https://gist.github.com/larrybolt/6295160).

Demo
----
![demo](https://cloud.githubusercontent.com/assets/5615415/8146876/dc64db98-1283-11e5-89d7-ca0b9532e0cd.png)

Usage
-----
1. Prerequisite - Create a A DNS record in your CloudFlare domain DNS Page.
![pre](https://cloud.githubusercontent.com/assets/5615415/8146875/d99d2366-1283-11e5-9082-1c3cfe333af6.png)
2. You also need your CloudFlare API Key. Get it from [your CloudFlare account settings page](https://www.cloudflare.com/a/account/my-account).
![key](https://cloud.githubusercontent.com/assets/5615415/8147337/c6614b06-1297-11e5-82f5-c2096442a2a3.png)
3. Download the `gen.py` script and run it. Please follow the descriptions.
  `wget https://raw.githubusercontent.com/pcchou/cf-ddns-gen/master/gen.py && chmod +x gen.py && ./gen.py`
