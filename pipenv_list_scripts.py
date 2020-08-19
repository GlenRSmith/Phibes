#!/usr/bin/env python
"""
Utility to allow pipenv command listing `scripts` from Pipfile
"""
try:
    import pipenv.core
except ModuleNotFoundError:
    print("This script is only for use in a development environment")
    exit(1)


def main():
    proj = pipenv.core.project
    if not proj:
        print("project not found")
        exit(1)
    scripts = proj.parsed_pipfile.get('scripts', [])
    print("command\tscript")
    for k, v in scripts.items():
        print(f"{k}\t{v}")
    return


if __name__ == '__main__':
    main()
