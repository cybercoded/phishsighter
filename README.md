# ![Phishsighter Here logo](https://github.com/kunley247/phishsighter/blob/main/static/image.jpg) 


### Table of Contents
**[Installation Instructions](#installation-instructions)**<br>
**[Usage Instructions](#usage-instructions)**<br>
**[Compatibility](#compatibility)**<br>
**[Building the Browser Extension](#building-the-extension-bundles)**<br>
**[Help and support](#help-and-support)**<br>


## Installation Instructions
```bash
  git clone http://github.com/kunley247/phishsighter
  cd phishsighter
  python -m env myvenv
  source ./myvenv/Script/activate
  pip install -r requirements.txt
```

## Usage Instructions
For the Web App
  ```bash
    python phishsighter.py --web
  ```

# ![Web Application](https://github.com/kunley247/phishsighter/blob/main/screenshots/gui.png) 

For the Command Line Interface
  ```bash
    python phishsighter.py --url="https://example.com"
  ```

# ![Command Line Interface](https://github.com/kunley247/phishsighter/blob/main/screenshots/cli.png) 

1. For Browser Extension and Notification
# ![Browser Extension and Notification](https://github.com/kunley247/phishsighter/blob/main/screenshots/broswer-extension-and-notification.png) 

## Compatibility
1. Make sure you are using Python 3.12.6 version in a Virtual Environment (env) to avoid unnecessary errors
2. The Browser extension was only tested in google chrome browser.

## Building the Browser Extension
1. Step 1: Enable the Developer Mode and click on load unpacked (this is the extension folder in the cloned repositories "https://github.com/kunley247/phishsighter/tree/main/extension"). just select the folder the then the extension will be unpacked into your chrome browser.

# ![Step 1 of Browser Extension Installation](https://github.com/kunley247/phishsighter/blob/main/screenshots/browser-extension.png) 

1. Step 2: Pin the extension to your browser tools bar
# ![Step 2 of Browser Extension Installation](https://github.com/kunley247/phishsighter/blob/main/screenshots/browser-extention-step3.png) 


## Help and support
If you have any question feel free to reach out to me on my personal email: ```cafeat9ja@gmail.com```