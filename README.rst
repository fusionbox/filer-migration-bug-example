filer-migration-bug-example
---------------------------

This project exists to illustrate a bug in migrations caused in django-filer.

What is the bug in filer
========================

According to a conversation in #django-dev, the behavior that Filer was
relying on is not supported in the new migration system.

Basically, the ``FilerFileField`` previously was overriding the ``to``
parameter with a model, like this:

.. code-block:: python

    from filer.models import File

    class FilerFileField(models.ForeignKey):
        def __init__(self, **kwargs):
            # Simplified for illustrative purposes.
            kwargs['to'] = File
            super(FilerFileField, self).__init__(**kwargs)


It was suggested in the IRC logs to change that to just a string, like this:

.. code-block:: python

    class FilerFileField(models.ForeignKey):
        def __init__(self, **kwargs):
            # Simplified for illustrative purposes.
            kwargs['to'] = 'filer.File'
            super(FilerFileField, self).__init__(**kwargs)

This will not cause the error.

How to reproduce
================

You can download this repository and run the following steps. ::

    $ virtualenv filer-migration-bug
    $ pip install -r requirements.txt
    $ python manage.py migrate

You should get a backtrace like this::

    File "manage.py", line 10, in <module>
      execute_from_command_line(sys.argv)
    File "/XXX/local/lib/python2.7/site-packages/django/core/management/__init__.py", line 338, in execute_from_command_line
      utility.execute()
    File "/XXX/local/lib/python2.7/site-packages/django/core/management/__init__.py", line 330, in execute
      self.fetch_command(subcommand).run_from_argv(self.argv)
    File "/XXX/local/lib/python2.7/site-packages/django/core/management/base.py", line 390, in run_from_argv
      self.execute(*args, **cmd_options)
    File "/XXX/local/lib/python2.7/site-packages/django/core/management/base.py", line 441, in execute
      output = self.handle(*args, **options)
    File "/XXX/local/lib/python2.7/site-packages/django/core/management/commands/migrate.py", line 221, in handle
      executor.migrate(targets, plan, fake=fake, fake_initial=fake_initial)
    File "/XXX/local/lib/python2.7/site-packages/django/db/migrations/executor.py", line 104, in migrate
      state = migration.mutate_state(state, preserve=do_run)
    File "/XXX/local/lib/python2.7/site-packages/django/db/migrations/migration.py", line 83, in mutate_state
      operation.state_forwards(self.app_label, new_state)
    File "/XXX/local/lib/python2.7/site-packages/django/db/migrations/operations/fields.py", line 183, in state_forwards
      state.reload_model(app_label, self.model_name_lower)
    File "/XXX/local/lib/python2.7/site-packages/django/db/migrations/state.py", line 100, in reload_model
      related_models = get_related_models_recursive(old_model)
    File "/XXX/local/lib/python2.7/site-packages/django/db/migrations/state.py", line 57, in get_related_models_recursive
      rel_app_label, rel_model_name = rel_mod._meta.app_label, rel_mod._meta.model_name
    AttributeError: 'NoneType' object has no attribute '_meta'


What is happening
=================

(here be dragons)

1. `django.db.migrations.state.get_related_models_recursive`_ was being called
   with ``yyy.Widget``, which would start to build a queue that contained
   ``filer.File``, but a reference to the real model, not the fake model (aka
   historical model).

2. Then ``get_related_models_recursive`` would recurse and get the related
   models for ``filer.File``, which end up calling
   ``Widget2._meta.get_fields``.

3. When ``get_fields`` is called on a fake model, it returns a list of fields
   that does not contain any virtual fields; however, when called on a **real**
   model, there are virtual fields, which means the ``Widget2.content`` was
   being accessed.

4. The related_model attribute of GenericForeignKey is ``None``, which is where
   we are getting the AttributeError from.


.. _django.db.migrations.state.get_related_models_recursive: https://github.com/django/django/blob/69ddc1b3da043195a0f4e09211d395724b42c70b/django/db/migrations/state.py#L32-L60


What can we can do to fix it
============================

There are two courses of action that we can take to fix this behavior:

1. Change filer not to set the ``to`` value to a direct model reference,
   instead we can set it to a string, like ``'filer.Filer'``.

2. Change Django to allow setting ``to`` like this and to have it convert it
   automatically.
