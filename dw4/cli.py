import argparse
from dw4.state_manager import WorkflowManager

def main():
    parser = argparse.ArgumentParser(
        description="DW4: A modern, robust development workflow."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 'approve' command
    approve_parser = subparsers.add_parser(
        "approve", help="Approve the current stage and advance to the next."
    )

    # 'status' command
    status_parser = subparsers.add_parser(
        "status", help="Display the current status of the workflow."
    )

    args = parser.parse_args()
    manager = WorkflowManager()

    if args.command == "approve":
        manager.approve()
    elif args.command == "status":
        manager.get_status()

if __name__ == "__main__":
    main()
