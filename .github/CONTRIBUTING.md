## Contributing to kmos

The kmos project welcomes contributions from everyone. There are a
number of ways you can help:

## Git and Pull requests
* Contributions are submitted, reviewed, and accepted using Github pull requests. [Read this article](https://help.github.com/articles/using-pull-requests) for some details. We use the _Fork and Pull_ model, as described there.
* The latest changes are in the `develop https://github.com/mhoffman/kmos/tree/develop`_ branch.
* Make a new branch for every feature `feature_<...>` you're working on.
* Try to make clean commits that are easily readable (including descriptive commit messages!)
* Test before you push. Get familiar with `Nosetest <http://nose.readthedocs.io/en/latest/>`_ , our test suite. Ideally create your own free account on [Travis](https://travis-ci.org/) and test your branch on it.
* Make small pull requests that are easy to review but make sure they do add value by themselves.

## Coding style
* Do write comments. You don't have to comment every line, but if you come up with something thats a bit complex/weird, just leave a comment. Bear in mind that you will probably leave the project at some point and that other people will read your code. Undocumented huge amounts of code are nearly worthless!
* run `pep8` or `autopep8` or even `autopep8` again your changes
* stick to [Google's Python style guide](https://google.github.io/styleguide/pyguide.html)
* Don't overengineer. Don't try to solve any possible problem in one step, but try to solve problems as easy as possible and improve the solution over time!
* Do generalize sooner or later! (if an old solution, quickly hacked together, poses more problems than it solves today, refactor it!)
* Keep it compatible. Do not introduce changes to the public API, or configurations too lightly. Don't make incompatible changes without good reasons!

## Documentation
* The docs are in the [docs](docs) and [examples](examples) folders in the git repository, so people can easily find the suitable docs for the current git revision.
* Documentation should be kept up-to-date. This means, whenever you add a new API method, add a new hook or change the database model, pack the relevant changes to the docs in the same pull request.

## Bug Reports

When opening new issues or commenting on existing issues please make
sure discussions are related to concrete technical issues with the
kmos software.

It's imperative that issue reports outline the steps to reproduce
the defect. If the issue can't be reproduced it will be closed.
Please provide [concise reproducible test cases](http://sscce.org/)
and describe what results you are seeing and what results you expect.

## Documentation

The official documentation of kmos resides at
[**ReadTheDocs.org**](https://kmos.rtfd.org).

## Code Contributions

The kmos project welcomes new contributors. Individuals making
significant and valuable contributions over time are made
[_Co-developers_](http://mhoffman.github.io/kmos/)

This document will guide you through the contribution process.

### Step 1: Fork

Fork the project [on Github](https://github.com/mhoffman/kmos)
and check out your copy locally.

```text
% git clone git@github.com:username/kmos.git
% cd kmos
% git remote add upstream git://github.com/mhoffman/kmos.git
```

#### Dependencies

We bundle dependencies in the _third-party/_ directory that is not
part of the project proper. Any changes to files in this directory or
its subdirectories should be sent upstream to the respective projects.
Please don't send your patch to us as we cannot accept it.

We do accept help in upgrading our existing dependencies or removing
superfluous dependencies. If you need to add a new dependency it's
often a good idea to reach out to the committers on the IRC channel or
the mailing list to check that your approach aligns with the project's
ideas. Nothing is more frustrating than seeing your hard work go to
waste because your vision doesn't align with the project's.

### Step 2: Branch

Create a feature branch and start hacking:

```text
% git checkout -b feature_<name>
```

We practice HEAD-based development, which means all changes are applied
directly on top of master.

### Step 3: Commit

First make sure git knows your name and email address:

```text
% git config --global user.name 'Santa Claus'
% git config --global user.email 'santa@example.com'
```

**Writing good commit messages is important.** A commit message
should describe what changed, why, and reference issues fixed (if
any).  Follow these guidelines when writing one:

1. The first line should be around 50 characters or less and contain a
   short description of the change.
2. Keep the second line blank.
3. Wrap all other lines at 72 columns.
4. Include `Fixes #N`, where _N_ is the issue number the commit
   fixes, if any.

A good commit message can look like this:

```text
explain commit normatively in one line

Body of commit message is a few lines of text, explaining things
in more detail, possibly giving some background about the issue
being fixed, etc.

The body of the commit message can be several paragraphs, and
please do proper word-wrap and keep columns shorter than about
72 characters or so. That way `git log` will show things
nicely even when it is indented.

Fixes #141
```

The first line must be meaningful as it's what people see when they
run `git shortlog` or `git log --oneline`.

### Step 4: Rebase

Use `git rebase` (not `git merge`) to sync your work from time to time.

```text
% git fetch upstream
% git rebase upstream/master
```

### Step 5: Test

Bug fixes and features **should have tests**. Look at other tests to
see how they should be structured.

Before you submit your pull request make sure you pass all the tests:

```text
% ./go clean test
```
