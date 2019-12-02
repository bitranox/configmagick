# STDLIB
import errno
import sys
from typing import List

# OWN
import lib_log_utils


class Config(object):
    pass


def main(sys_argv: List[str] = sys.argv[1:]) -> None:

    try:
        lib_log_utils.add_stream_handler_color()

    except FileNotFoundError:
        # see https://www.thegeekstuff.com/2010/10/linux-error-codes for error codes
        # No such file or directory
        sys.exit(errno.ENOENT)      # pragma: no cover
    except FileExistsError:
        # File exists
        sys.exit(errno.EEXIST)      # pragma: no cover
    except TypeError:
        # Invalid Argument
        sys.exit(errno.EINVAL)      # pragma: no cover
        # Invalid Argument
    except ValueError:
        sys.exit(errno.EINVAL)      # pragma: no cover


if __name__ == '__main__':
    main()                          # pragma: no cover
