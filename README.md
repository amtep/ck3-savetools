# ck3-savetools
Tools for extracting information from a Crusader Kings 3 savefile

To use this tool you generally need to write your own python script to extract and report the information you want.
This repository just provides the savefile scanning code. It's a base for development, not a finished tool.

It does NOT handle Ironman saves. Reading those requires a bit of secret Paradox information that I don't want to publish here.

The Python is pretty slow (about a minute to scan one savefile), but runninh it under pypy3 makes it only take a few seconds.
