from __future__ import absolute_import

import argparse
import os

from blessings import Terminal
term = Terminal()

from . import RepoConfigParser
from . import RepositoryHandler
from .git import git


def main():
    config_parser = argparse.ArgumentParser(
        description='Handle multiple scm repos.'
    )

    sub_parsers = config_parser.add_subparsers(title="action")

    # Init action
    init_parser = sub_parsers.add_parser(
        "init",
        help="Initialise a polygamy workspace"
    )
    init_parser.add_argument(
        'url',
        help='The url of the polygamy config repository you want to clone'
    )
    init_parser.add_argument('branch', nargs='?', default='master')
    init_parser.set_defaults(action='init')

    # Pull action
    pull_parser = sub_parsers.add_parser(
        'pull',
        help="Update your local repositories"
    )
    pull_parser.add_argument(
        '-n', '--dry-run', action='store_true',
        help=("Run in dry run mode. Remoted will be fetched, but"
              " configuration will not be updated, and branches will not be"
              " fast forwarded.")
    )
    pull_parser.set_defaults(action='pull')

    # Status action
    status_parser = sub_parsers.add_parser(
        'status',
        help=("Shows the current status of your repositories. Included the"
              " branch you're on, the number of commits you're head of the"
              " default remote branch, and how many commits you are behind.")
    )
    status_parser.set_defaults(action='status')

    # Fetch action
    fetch_parser = sub_parsers.add_parser(
        'fetch',
        help=("Fetches changes from the remote repository. This will not"
              " clone new repositories, or fast-forward exsiting"
              " repositories.")
    )
    fetch_parser.set_defaults(action='fetch')

    # List action
    list_action = sub_parsers.add_parser(
        'list',
        help="Lists the repositories under control by polygamy."
    )
    list_action.add_argument(
        '-s', '--seperator',
        default='\n',
        help=("String to seperate the repositories with. Defaults to a new"
              " line.")
    )
    list_action.add_argument(
        '-l', '--local-only',
        action='store_true',
        help=("Only list repositories that have local changes.")
    )
    list_action.set_defaults(action='list')

    # List action
    push_action = sub_parsers.add_parser(
        'push',
        help=("Pushes the current branch to the remote. Note: this does a"
              " simple push. I.e the local branch name will be the branch"
              " that will be pushed to on the remote.")
    )
    push_action.add_argument(
        'repositories',
        type=str,
        nargs='+',
        help="The repositories to push."
    )
    push_action.set_defaults(action='push')

    args = config_parser.parse_args()

    if args.action == 'init':
        os.mkdir('.polygamy')
        git.clone('.polygamy/polygamy', args.url, args.branch)

    parser = RepoConfigParser.JsonConfigParser()
    parser.find_config_file(path=os.getcwd())
    parser.parse_file()
    repository_handler = RepositoryHandler.GitRepositoryHandler(
        config=parser,
        dry_run=getattr(args, 'dry_run', False)
    )

    if args.action in ('pull', 'init'):
        repository_handler.update_repositories()
    elif args.action == 'status':
        repository_handler.status()
    elif args.action == 'fetch':
        repository_handler.fetch()
    elif args.action == 'list':
        repository_handler.list(args.seperator, args.local_only)
    elif args.action == 'push':
        repository_handler.push(args.repositories)
