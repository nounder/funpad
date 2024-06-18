# Ideas

## prompt_toolkit

it's more extensible than ipython and allows to build more
sophisticated interfaces rather than just a REPL

easy to integrate with asyncio

<https://python-prompt-toolkit.readthedocs.io/en/master/pages/advanced_topics/styling.html>

## bpython

it's not compatible with prompt_toolkit ecosystem but has great
built-in features like docstring previews

<https://github.com/bpython/bpython/>

<https://bpython-interpreter.org/screenshots.html>

## html result frontend

tutorial for html page dump:
<https://ipywidgets.readthedocs.io/en/latest/embedding.html>

render single ipywidget output:
<https://github.com/jupyter-widgets/ipywidgets/blob/main/packages/html-manager/src/libembed.ts#L51>

output component from jupyterlab
https://github.com/jupyterlab/jupyterlab/tree/main/packages/outputarea

ipywidget seems to be compatible with IPython.display.

## render html output

auto refresh on change?

## use kitty icat for ipython prompt?

if function returns ipython.display.Image, print it
in terminal

try it in a prompt:

import subprocess
subprocess.run(["/opt/homebrew/bin/kitty", "icat", "image.png"])

imgcat used by iterm2:

https://github.com/wookayin/python-imgcat

kitty support in progress for 4yr now
