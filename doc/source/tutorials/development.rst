Development
===========


Contributions of any sort are of course quite welcome.
Patches and comments are ideally sent in form of email,
pull request, or github issues.

To make synergizing a most pleasing experience I suggest you use
git, nose, pep8, and pylint ::

  sudo apt-get install git python-nose pep8 pylint

When sending a patch please make sure the nose tests pass, i.e. run
from the top project directory ::

  nosetests


To make testing and comparison even easier it would be helpful if you
create an account with `Travis CI <https://travis-ci.org/>`_ and run your
commits through the test suite.

Have a look at Google's Python `style guide <https://google.github.io/styleguide/pyguide.html>`_ as far as style questions go.
