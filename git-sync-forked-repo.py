#!/usr/bin/env python3

import sys
import os
import subprocess
from tempfile import TemporaryDirectory
from argparse import ArgumentParser


WHITE = '\u001b[37;1m'
CYAN = '\u001b[36;1m'
RESET = '\u001b[0m'


def log(msg, color=WHITE):
    print(color, msg, RESET, sep='')


def cmd(cmdline, return_output=False):
    log('>>> %s' % cmdline, color=CYAN)
    func = subprocess.check_output if return_output else subprocess.check_call
    return func(cmdline, shell=True, text=True)


def main():
    parser = ArgumentParser(description='Sync branches from source repository into target repository using rebase')
    parser.add_argument('target_repo_url', help='Forked repository where new commits should be written to')
    parser.add_argument('source_repo_url', help='Original repository where new commits should be taken from')
    return run(parser.parse_args())


SOURCE_REMOTE = 'source_repo'


def run(args):
    workdir = TemporaryDirectory().name
    log('Cloning target repository')
    cmd('git clone %s %s' % (args.target_repo_url, workdir))
    os.chdir(workdir)
    # Add global repository as new remote
    if '%s\t' % SOURCE_REMOTE not in cmd('git remote -v', return_output=True):
        log('Adding source repository as an additional remote')
        cmd('git remote add %s %s' % (SOURCE_REMOTE, args.source_repo_url))
        cmd('git fetch %s' % SOURCE_REMOTE)
    # Sync each branch
    origin_branches = set(branch.strip()[7:] for branch in cmd('git branch -r | egrep "^  origin/"',
                                                               return_output=True).splitlines())
    local_branches = set(branch[2:] for branch in cmd('git branch', return_output=True).splitlines())
    for branch in cmd('git branch -r | egrep "^  %s/"' % SOURCE_REMOTE, return_output=True).splitlines():
        branch = branch.strip()[len(SOURCE_REMOTE)+1:]
        log('\nBranch %s' % branch)
        # Checkout
        if branch in origin_branches:
            if branch in local_branches:
                cmd('git checkout %s' % branch)
            else:
                cmd('git checkout --track origin/%s' % branch)
            cmd('git rebase %s/%s' % (SOURCE_REMOTE, branch))
        elif branch in local_branches:
            raise RuntimeError('Something is weird, %s is a local branch, but belongs to source repo')
        else:  # Branch exists only on source repo
            cmd('git checkout %s' % branch)
        cmd('git push -u origin %s' % branch)
        # Push this branch
        cmd('git log --oneline --decorate=full -1')
    # Push tags
    cmd('git push --tags origin')


if __name__ == '__main__':
    sys.exit(main())
