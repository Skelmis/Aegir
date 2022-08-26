# Aegir

Aegir (Pronounced a-gur) is an auto-migration tool for migrating nextcord bots using version 2 over to version 3.

#### Formatting Errors

`.errors` will currently handle and fix the following:

- `event` decorators being called
- `listen` decorators not being called
- failure to process commands when using `on_message` as an event

Runs on Python 3.10.