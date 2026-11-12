Pure Python Jeelink LaCrosse Library
====================================

|PypiVersion| |PyPiPythonVersions| |Coveralls| |CodeClimate|


Requirements
------------

This library works with the `Jeelink`_ USB RF adapter and the Arduino `sketch`_ hosted on the `FHEM`_ website.

Tested Devices
--------------
* Technoline TX 29IT
* Technoline TX 29DTH-IT

Command Line Tool
-----------------

.. code :: shell

    # pylacrosse -h
    usage: LaCrosse sensor CLI tool. [-h] [-v] [-d DEVICE] [-f FREQUENCY_RFM1]
                                     [-F FREQUENCY_RFM2] [-t TOGGLE_INTERVAL_RFM1]
                                     [-T TOGGLE_INTERVAL_RFM2]
                                     [-m TOGGLE_MASK_RFM1] [-M TOGGLE_MASK_RFM2]
                                     [-r DATARATE_RFM1] [-R DATARATE_RFM2]
                                     {scan,info,led} ...

    optional arguments:
      -h, --help            show this help message and exit
      -v                    be more verbose
      -d DEVICE, --device DEVICE
                            set local device e.g. '/dev/ttyUSB0' or
                            set remote device e.g. 'rfc2217://[IP]:[PORT]'
                            default: '/dev/ttyUSB0'
      -f FREQUENCY_RFM1     set the frequency for RFM1
      -F FREQUENCY_RFM2     set the frequency for RFM2
      -t TOGGLE_INTERVAL_RFM1
                            set the toggle interval for RFM1
      -T TOGGLE_INTERVAL_RFM2
                            set the toggle interval for RFM2
      -m TOGGLE_MASK_RFM1   set the toggle mask for RFM1
      -M TOGGLE_MASK_RFM2   set the toggle mask for RFM2
      -r DATARATE_RFM1      set the datarate for RFM1
      -R DATARATE_RFM2      set the datarate for RFM2

    Commands:
      {scan,info,led}
        scan                Show all received sensors
        info                Get configuration info
        led                 Set traffic LED state


The LaCrosse sensor generates the ID every time the battery is changed.

Use the cli tool ``pylacrosse`` to find your device:

.. code :: shell

    # pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=unknown
    id=16 t=18.700000 h=60 nbat=0 name=unknown
    id=0 t=17.400000 h=65 nbat=0 name=unknown

You can generate a file with know devices at ``~/.lacrosse/known_sensors.ini``

.. code :: shell

    [0]
    name = Kitchen
    [16]
    name = Livingroom
    [40]
    name = Bedroom

then the tool will print the defined names

.. code :: shell

    # pylacrosse -d /dev/ttyUSB0 scan
    id=40 t=16.000000 h=69 nbat=0 name=Bedroom
    id=16 t=18.700000 h=60 nbat=0 name=Livingroom
    id=0 t=17.400000 h=65 nbat=0 name=Kitchen

Using remote serial port with ser2net
-------------------------------------

You can also use ``ser2net`` to connect to a remote JeeLink Adapter. This can be useful, if you use
a Docker container or if you can not attach a JeeLink adapter to your host running ``pylacrosse``. On your
remote device install ``ser2net`` and add the following line to your ``ser2net.conf`` file:

.. code :: shell

    20001:telnet:0:/dev/ttyUSB0:57600 remctl banner

Restart the ``ser2net`` daemon and connect to your remote host using ``pylacrosse`` command line tool:

.. code :: shell

    # pylacrosse -d rfc2217://[REMOTE_IP]]:20001 scan
    id=40 t=16.000000 h=69 nbat=0 name=Bedroom
    id=16 t=18.700000 h=60 nbat=0 name=Livingroom
    id=0 t=17.400000 h=65 nbat=0 name=Kitchen

Publishing
----------

The ``release.yml`` workflow is restricted to ``vipwolf/python-lacrosse``.
Pushes to ``main`` and ``develop`` build and publish to TestPyPI. Pull requests,
other branches, and manual runs do not trigger it. Pushing a canonical
``X.Y.Z`` tag publishes only to PyPI, after environment approval. The tagged
commit must be in ``main`` history. Lightweight and annotated tags are
supported; prefixes such as ``v`` and leading zeroes are rejected.

Branch builds use ``0.0.<run_id>.dev<run_attempt>``, a TestPyPI-only namespace
without local versions or collisions across branches and retries. Release
versions come from the existing Hatch VCS configuration and must match the
tag exactly. Reuploading a PyPI version fails instead of skipping files.
Artifacts expire after seven days; monitor TestPyPI's project storage quota.

One-Time Setup
~~~~~~~~~~~~~~

Complete these settings before enabling publishing. Naming an environment
in YAML does not configure its protection rules.

1. Verify ownership of ``pylacrosse`` on both indexes. Owning this GitHub fork
    does not grant ownership of the upstream PyPI project. An existing project
    owner must authorize the publisher; pending publishers only work for an
    available project name.
2. Under GitHub **Settings > Environments**, create ``pypi``. Enable
    **Required reviewers**, select a trusted maintainer, enable **Prevent
    self-review**, and disable administrator bypass. Under **Deployment
    branches and tags**, select **Selected branches and tags** and allow only
    tags matching ``[0-9]*.[0-9]*.[0-9]*``. The workflow additionally enforces
    exact syntax and ancestry. Independent review needs a second maintainer;
    do not silently disable this control for a solo release.
3. Create ``testpypi`` without required approval. Allow only the branch refs
    ``main`` and ``develop``, with no permitted tag refs. Neither environment
    needs secrets. Required-reviewer availability for private repositories
    depends on the GitHub plan; confirm support before activation.
4. On each index, open the project's **Publishing** settings and add a GitHub
    Trusted Publisher: owner ``vipwolf``, repository ``python-lacrosse``,
    workflow filename ``release.yml``, and environment ``pypi`` or ``testpypi``
    respectively. Use pending publishers only for new projects. Remove and
    revoke old publishing tokens after migrating.
5. Under **Settings > Rules > Rulesets**, activate rules for ``main`` and
    ``develop`` requiring pull requests and independent review, dismissing
    stale approvals, and preventing force pushes and deletion. Avoid broad
    bot/admin bypass. Do not require this publishing workflow as a PR check:
    it does not run on PRs. Require maintainer review of workflows, dependency
    locks, build hooks, and package changes; configure code ownership with your
    actual reviewers.
6. Create a tag ruleset for ``[0-9]*.[0-9]*.[0-9]*`` restricting creation,
    with only release maintainers on its bypass list. Separately create an
    immutable-tag ruleset with no bypass, restricting updates and deletions
    and blocking force pushes. This permits creation without replacement.
7. Keep the default GitHub token read-only, disable Actions creating or
    approving PRs, and restrict allowed actions to reviewed immutable refs.
    Use MFA/passkeys, review app and personal-token access, and review Trusted
    Publishers when offboarding maintainers.

Release Verification
~~~~~~~~~~~~~~~~~~~~

First verify an authorized branch push on TestPyPI: inspect both distributions,
the version, and PEP 740 attestations. For an actual release, push an unused
``X.Y.Z`` tag on ``main`` history. Under **Actions > workflow run > Review
deployments**, check the commit and artifacts before approving ``pypi``.
Do not publish fake production versions to test authentication.

Builds and installed-wheel tests run in an unprivileged job. Publishing jobs
only download this run's artifact by ID and invoke the official PyPA container
using short-lived OIDC authentication. They do not check out code or install
the package. The Linux/amd64 publisher image is pinned by manifest digest from
PyPA's ``v1.14.3`` image tag, instead of using the standard wrapper's mutable
container tag. All input defaults are explicit; attestations and metadata
checks are enabled, duplicates are fatal, and verbose debugging is disabled.

Maintaining Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

The release environment uses Python 3.11 and the ``release`` dependency group
in ``pyproject.toml``, resolved with package hashes in ``uv.lock``. The workflow
pins both the setup-uv action commit and the uv archive checksum, and disables
shared caches. Use a reviewed ``uv`` installation to update release dependencies:

.. code:: shell

    uv lock --upgrade-group release --default-index https://pypi.org/simple

Review changed versions, hashes, and security advisories. Synchronize with
``uv sync --locked --no-default-groups --group release --no-install-project
--no-build --python 3.11``. This installs only locked wheels, not the project.
Build using ``uv build --no-build-isolation --python <environment>/bin/python
--no-create-gitignore`` so build backends come from that locked environment.
Do not add a TestPyPI extra index or let isolation resolve unpinned backends.
Check distributions with ``python -m twine check --strict dist/*`` and test
the wheel outside the checkout, installing it with ``uv pip install --no-deps
--no-index`` into the same environment. Updating uv also requires reviewing
and changing its version and archive checksum together in the workflow.

Dependabot proposes weekly action updates without automatic merges. Review
upstream commits and source. After action changes, regenerate
``.github/workflows/actions.lock`` using the official, reviewed
``github/gh-actions-lock`` extension and ``gh actions-lock``. Never hand-edit
the generated lock. The generator rewrites action references to version tags;
restore the corresponding reviewed full commit SHAs in the workflow afterward
to retain explicit pins as well. Check with ``gh actions-lock --verify`` and
``gh actions-lock --verify-local``. These accept explicit SHAs with a warning
that the generator prefers tag references. Generation and online verification
require GitHub authentication. The action lock does not pin runner images,
Python runtime downloads, or container images.

Update the ``docker://`` publisher digest manually in both publishing steps.
Resolve the official ``ghcr.io/pypa/gh-action-pypi-publish`` release image,
inspect source/platform metadata, and verify its manifest digest. Never resolve
a mutable image tag during a release. Verify updates through TestPyPI first.

After changes, run ``python -m pytest``,
``actionlint .github/workflows/release.yml``, and
``zizmor .github/workflows/release.yml``. Policy tests cover rejected events,
forks, tag syntax and ancestry, checkout identity, and development retries.

This follows the `PyPA publishing guide`_ and addresses mutable dependencies,
privileged untrusted builds, shell injection, and stolen maintainer credentials
highlighted in the `2026 workflow attack report`_ and `WFX incident report`_.
Pins establish integrity, not benign content; attestations identify publishers,
not whether code is malware-free. Compromised approvers, trusted dependencies,
or GitHub/PyPI services remain risks. This workflow does not claim reproducible
runner images or network egress enforcement.

.. _PyPA publishing guide: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
.. _2026 workflow attack report: https://www.stepsecurity.io/blog/hackerbot-claw-github-actions-exploitation
.. _WFX incident report: https://www.stepsecurity.io/blog/wfx-phantom-the-github-actions-secret-stealer

.. _Jeelink: https://www.digitalsmarties.net/products/jeelink
.. _sketch: https://svn.fhem.de/trac/browser/trunk/fhem/contrib/arduino/36_LaCrosse-LaCrosseITPlusReader.zip
.. _FHEM: https://wiki.fhem.de/wiki/JeeLink

.. |PyPiVersion| image:: https://badge.fury.io/py/pylacrosse.svg
                 :target: http://badge.fury.io/py/pylacrosse
.. |PyPiPythonVersions| image:: https://img.shields.io/pypi/pyversions/pylacrosse.svg
                        :alt: Python versions
                        :target: http://badge.fury.io/py/pylacrosse
.. |CodeClimate| image:: https://api.codeclimate.com/v1/badges/fc83491ef0ae81080882/maintainability
                 :target: https://codeclimate.com/github/hthiery/python-lacrosse/maintainability
                 :alt: Maintainability
.. |Coveralls|   image:: https://coveralls.io/repos/github/hthiery/python-lacrosse/badge.svg?branch=master
                 :target: https://coveralls.io/github/hthiery/python-lacrosse?branch=master
