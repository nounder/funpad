import sys
import inspect
import logging
import threading
import inspect
from typing import Generator
import weakref
import watchfiles
from traitlets.config import Config
import IPython
import rich
import rich.traceback

rich.traceback.install(show_locals=True)


PATH = sys.argv[1] if len(sys.argv) > 1 else "."

RichConsole = rich.console.Console()


logger = logging.Logger(__name__)
logger.setLevel(logging.DEBUG)


def load_module(path: str, *, name="funpad.user.scratch"):
    """
    See: https://stackoverflow.com/questions/67631

    TODO: Use runpy maybe?
    """
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)

    # I don't think this is necesssary
    # May be used only for caching?
    # sys.modules[name] = module

    spec.loader.exec_module(module)

    return module


class FileWatcher:
    path: str
    thread: threading.Thread = None
    event = threading.Event()

    def __init__(self, path):
        self.path = path

    def watch_file_changes(self):
        for _ in watchfiles.watch(self.path):
            self.event.set()

    def wait(self):
        self.event.wait()
        self.event.clear()

    def start(self):
        self.thread = threading.Thread(
            target=self.watch_file_changes, name="file_watcher"
        )
        self.thread.daemon = True
        self.thread.start()

        return self


class Runner:
    scrach_module_name = "funpad.user.scratch"
    thread: threading.Thread = None
    i = 0
    ready_event = threading.Event()
    base_locals = {}
    local_sources = weakref.WeakKeyDictionary()

    def __init__(self, path, *, locals=None):
        self.locals = locals
        self.path = path

    def _execute(self):
        self._iter()

        # self.ready_event.set()

        for _ in watchfiles.watch(self.path):
            self._iter()

    def _filter_member(self, key, value, old_value):
        if key.startswith("__"):
            return False

        source = self._get_source(value)

        if source:
            module = getattr(value, "__module__", None)

            if module and module.startswith(self.scrach_module_name + "_"):
                if old_value:
                    try:
                        old_source = self.local_sources.get(old_value)
                        new_source = self._get_source(value)

                        logger.debug("Old source: %s", old_source)
                        logger.debug("New source: %s", new_source)

                        if old_source == new_source:
                            return False

                    except TypeError as e:
                        logger.error(e)

        if old_value == value:
            return False

        return True

    def _iter(self):
        # self.i += 1

        iter_locals = {}

        try:
            module_name = self.scrach_module_name + "_" + str(self.i)
            module = load_module(self.path, name=module_name)

            iter_locals = inspect.getmembers(module)
        except Exception as e:
            # TODO: print pretty stacktrace
            raise e

            logging.error(e)

        new_locals = {}

        for key, value in iter_locals:
            old_value = self.base_locals.get(key)

            if not self._filter_member(key, value, old_value):
                continue

            new_locals[key] = value

        rich.print("New locals:", new_locals)

        for value in new_locals.values():
            source = self._get_source(value)

            try:
                self.local_sources[value] = source
            except TypeError:
                # Handle primitives values which cannot be weakly references
                pass

        self.locals.update(new_locals)

        self.base_locals.update(new_locals)

        main_fn = self.base_locals.get("main")

        if main_fn:
            print("Executing main...", end="")

            try:
                res = main_fn()

                if res:
                    print()
                    rich.print(res)
                else:
                    print(" Done")

            except Exception as e:
                RichConsole.print_exception()

    def start(self):
        self.thread = threading.Thread(target=self._execute, name="script_runner")
        self.thread.daemon = True
        self.thread.start()

        return self

    def _get_source(self, object):
        try:
            source = inspect.getsource(object)
        except TypeError:
            # TODO: consider hashing objects without source
            # like compiled functions
            # source = hash(source)
            source = None

        return source


# runner.ready_event.wait(i

# # doesnt work
# config = Config()
# config.InteractiveShellApp.extensions = ["autoreload", "rich"]
# config.InteractiveShellEmbed.extensions = ["autoreload", "rich"]
# config.TerminalInteractiveShell.extensions = ["autoreload", "rich"]


def start_ipython(local_ns):
    from IPython.terminal.ipapp import TerminalIPythonApp

    app = TerminalIPythonApp(
        argv=[],
        colors="neutral",
        header="None",
        confirm_exit=False,
        user_ns=local_ns,
        display_banner=False,
    )

    app.initialize(argv=[])

    app.shell.run_cell("%pdb", store_history=False)
    app.shell.run_cell("%load_ext rich", store_history=False)

    globals()["ipy"] = app
    app.start()


def main():
    globals()["i"] = rich.inspect

    local_ns = locals()

    runner = Runner(PATH, locals=local_ns).start()

    start_ipython(local_ns)


if __name__ == "__main__":
    main()
