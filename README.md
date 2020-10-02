# uwcs-zarya

### Content's
* [About](#about)
* [Installation](#installation)
  * [Dependencies](#dependencies)
  * [Installation and Configuration](#installation-and-configuration)
* [License](#license)

### About
uwcs-zarya is the newest variant of the University of Warwick Computing Society website, built for the 2016-17 academic year. The site is built upon Python, using Django and the [Wagtail CMS](https://github.com/torchbox/wagtail).

The name 'Zarya' comes from the Overwatch character of the same name. The previous website, named 'Reinhardt', shares a name with another character within Overwatch - both of the same class. However the previous website pre-dates Overwatch by a significant amount of time, with the name actually deriving from the musician [Django Reinhardt](https://en.wikipedia.org/wiki/Django_Reinhardt).

### Installation
This section details the deployment of uwcs-zarya on a Linux system.

#### Dependencies
uwcs-zarya depends upon a variety of softwares though at its core the website is built upon the Django web framework. The list of dependencies are:

* Python 3.5
* Redis
* Sass (Ruby)
* Bower (npm/node)
* Postgresql
* Virtualenv
* Supervisor

The deployment of the website on the UWCS systems also uses Apache 2 and mod_wsgi for a web server, though it would be possible to use nginx too. The site also uses a transactional email provided for email, though normal SMTP can be used and configured using Django's standard configuration settings.

#### Installation and Configuration
With the packaged dependencies installed and configured (most/all should be available with any Linux distribution's package manager), the steps for installation of the website are as follows, though you may want to stop after step 5 if you are not going to deploy the website for production purposes:

1. (Optional) Create a virtualenv to run the server from - make sure it's using python 3.5
2. `git clone` the repository to the location you wish to serve the site from (e.g: `/var/www/uwcs-zarya`)
3. Install the requirements using `pip -r requirements.txt` (make sure you're using the virtualenv if you're using one)
4. `cd uwcs-zarya/zarya/settings` and create an appropriate settings file `production.py` from the provided sample `production.py.example`
5. `cd uwcs-zarya/` and bring the backend database up to speed by running `python manage.py migrate` - if you're using a virtualenv do make sure you are running python from it
6. `cd uwcs-zarya/zarya/components` and then install the Bower dependencies using `bower install` (if you are not deploying for production, you may skip to point 11 at the end of the list)
7. `cd uwcs-zarya/` and run `python manage.py compress --force` and `python manage.py collectstatic`, accepting where applicable
8. Create a directory `uwcs-zarya/media`, ensuring your web server has sufficient access to this folder (`rwx` permissions)
9. Create the appropriate configuration files for Supervisor to run Celery automatically and allow it to recover on restart
10. Create the configuration file(s) for the web server of your chosing
11. Run your web server (if you're developing locally, simply run `python manage.py runserver`

#### Ubuntu 16.04 Xenial development setup

If you blindly follow these instructions, you should have a working instance of the website.

Setup postgres database:
```
sudo apt-get install postgresql
sudo -u postgres createuser -D -A -P zarya
(enter 'password' as password)
sudo -u postgres createdb -Ozarya zarya
```

Install systemwide runtime/build dependencies:
```
sudo apt-get install virtualenv postgresql-server-dev-9.5 build-essential python3-dev redis ruby-sass
```

The nodejs in the default ubuntu repositories is too old so you have to do:
```
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Create python virtualenv and install python dependencies:
```
virtualenv -p /usr/bin/python3 zarya-env
. ./zarya-env/bin/activate
pip install -r requirements.txt
```

Fetch bower components:
```
cd zarya/components
npm install bower
./node_modules/.bin/bower install
```

Seed the database:
```
python ./manage.py migrate
python ./manage.py createsuperuser
```

At this point you can get a repl using:
```
python ./manage.py shell
```

Run these to create the basic site structure:
```python
from wagtail.wagtailcore.models import Page, Site
from blog.models import HomePage, AboutPage
from events.models import EventsIndexPage

root = Page.objects.first()
home = root.add_child(instance=HomePage(title='UWCS Home', slug='home', description='UWCS Home', show_in_menus=True))
home.add_child(instance=AboutPage(title='Home', slug='home', show_in_menus=True))
home.add_child(instance=EventsIndexPage(title='Events', slug='events', show_in_menus=True))
Site.objects.create(hostname='localhost', port=8000, root_page=home, site_name='local', is_default_site=True)
```

Start development server:
```
python ./manage.py runserver
```

Go to http://localhost:8000 and you should see a basic instance of the site!

The last step is to start a celery worker for background tasks. Open a new terminal and run:

```
. ./bin/zarya-env/activate
celery -A zarya worker -l info
```

### License
This project is distributed under the MIT license.

The MIT License (MIT)
=====================

Copyright © 2016 David Richardson

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the “Software”), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
