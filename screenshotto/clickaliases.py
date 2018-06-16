"""
    Extension for the python ``click`` module
    to provide a group or command with aliases.
"""
# lightly edited from https://github.com/click-contrib/click-aliases
"""
Copyright (c) 2016 Robbin Bonthond

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import click


class ClickAliasedGroup(click.Group):
    def __init__(self, *args, **kwargs):
        super(ClickAliasedGroup, self).__init__(*args, **kwargs)
        self._commands = {}
        self._aliases = {}


    def command(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        decorator = super(ClickAliasedGroup, self).command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd


        return _decorator


    def group(self, *args, **kwargs):
        aliases = kwargs.pop("aliases", [])
        decorator = super(ClickAliasedGroup, self).group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd


        return _decorator


    def get_command(self, ctx, cmd_name):
        if cmd_name in self._aliases:
            cmd_name = self._aliases[cmd_name]
        command = super().get_command(ctx, cmd_name)
        if command:
            return command
        else:
            cmdnames = {x for x in self.list_commands(ctx)
                        if x.startswith(cmd_name)}
            aliases = {k: v for k, v in self._aliases.items()
                       if k.startswith(cmd_name)}
            funcnames = cmdnames.union(aliases.values())
            if not funcnames:
                return None
            elif len(funcnames) == 1:
                return super().get_command(ctx, funcnames.pop())
            aliasnames = set(aliases.keys()).union(cmdnames)
            ctx.fail("Too many matches: {} ".format(", ".join(aliasnames)))


    def format_commands(self, ctx, formatter):
        rows = []
        for sub_command in self.list_commands(ctx):
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue
            if hasattr(cmd, "hidden") and cmd.hidden:
                continue
            if sub_command in self._commands:
                aliases = ", ".join(sorted(self._commands[sub_command]))
                sub_command = "{0} ({1})".format(sub_command, aliases)
            cmd_help = cmd.short_help or ""
            rows.append((sub_command, cmd_help))
        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)
