"""Security configuration for Python code execution sandbox."""
import json
from typing import Dict, Any


def get_seccomp_profile() -> Dict[str, Any]:
    """
    Get seccomp security profile for Docker container.

    Restricts system calls to only those necessary for Python execution.

    Returns:
        Seccomp profile as dictionary
    """
    return {
        "defaultAction": "SCMP_ACT_ERRNO",
        "architectures": ["SCMP_ARCH_X86_64", "SCMP_ARCH_X86", "SCMP_ARCH_X32"],
        "syscalls": [
            {
                "names": [
                    # Essential syscalls for Python
                    "read", "write", "open", "close", "stat", "fstat",
                    "lstat", "poll", "lseek", "mmap", "mprotect", "munmap",
                    "brk", "rt_sigaction", "rt_sigprocmask", "rt_sigreturn",
                    "ioctl", "access", "pipe", "select", "mremap",
                    "msync", "mincore", "madvise", "dup", "dup2",
                    "nanosleep", "getpid", "clone", "fork", "vfork",
                    "execve", "exit", "wait4", "uname", "fcntl",
                    "fsync", "fdatasync", "getcwd", "chdir", "fchdir",
                    "getdents", "getdents64", "getrlimit", "getrusage",
                    "sysinfo", "times", "getuid", "getgid", "geteuid",
                    "getegid", "getppid", "getpgrp", "setsid",
                    "gettimeofday", "clock_gettime", "clock_getres",
                    "exit_group", "set_tid_address", "futex",
                    "set_robust_list", "get_robust_list",
                    "prctl", "arch_prctl", "gettid", "readlink",
                    "getrandom", "openat", "newfstatat", "fchmodat",
                    "faccessat", "pread64", "pwrite64", "readv", "writev",
                    "preadv", "pwritev", "preadv2", "pwritev2",
                    "eventfd2", "epoll_create1", "epoll_ctl", "epoll_wait",
                    "epoll_pwait", "signalfd4", "timerfd_create",
                    "timerfd_settime", "timerfd_gettime",
                ],
                "action": "SCMP_ACT_ALLOW"
            }
        ]
    }


def get_apparmor_profile() -> str:
    """
    Get AppArmor security profile for Docker container.

    Restricts filesystem and network access.

    Returns:
        AppArmor profile as string
    """
    return """
#include <tunables/global>

profile python-sandbox flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>
  #include <abstractions/python>

  # Allow Python interpreter and libraries
  /usr/bin/python3* ix,
  /usr/lib/python3*/** mr,
  /usr/local/lib/python3*/** mr,

  # Allow /tmp for temporary files only
  /tmp/** rw,
  /code.py r,

  # Deny network access
  deny network inet,
  deny network inet6,

  # Deny most filesystem access
  deny /home/** rw,
  deny /root/** rw,
  deny /etc/shadow r,
  deny /etc/passwd w,
  deny /sys/** w,
  deny /proc/sys/** w,
  deny /dev/** w,

  # Allow reading system files needed by Python
  /etc/ld.so.cache r,
  /etc/localtime r,
  /usr/share/zoneinfo/** r,
}
"""


def validate_code_safety(code: str) -> tuple[bool, str]:
    """
    Perform basic safety checks on submitted code.

    Args:
        code: Python code to validate

    Returns:
        Tuple of (is_safe, error_message)
    """
    # Check for dangerous imports
    dangerous_imports = [
        "os.system", "subprocess", "eval", "exec",
        "__import__", "compile", "open(",
        "socket", "urllib", "requests",
        "pickle", "shelve", "marshal",
    ]

    code_lower = code.lower()
    for dangerous in dangerous_imports:
        if dangerous in code_lower:
            return False, f"Potentially unsafe code detected: {dangerous}"

    # Check code length (prevent resource exhaustion)
    if len(code) > 10000:
        return False, "Code too long (max 10000 characters)"

    # Check for excessive loops (basic check)
    if code.count("while True:") > 1:
        return False, "Multiple infinite loops detected"

    return True, ""


def sanitize_output(output: str, max_length: int = 10000) -> str:
    """
    Sanitize execution output.

    Args:
        output: Raw output from code execution
        max_length: Maximum output length

    Returns:
        Sanitized output
    """
    if not output:
        return ""

    # Truncate if too long
    if len(output) > max_length:
        output = output[:max_length] + "\n... (output truncated)"

    # Remove any potential ANSI escape codes
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)

    return output
