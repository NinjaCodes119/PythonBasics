"""A simple command-line task manager.

Tasks are saved to a JSON file (tasks.json by default) so they persist
between runs. Uses only the Python standard library.

Usage examples:
    python task_manager.py add "Buy milk"
    python task_manager.py add "Finish report" --priority high
    python task_manager.py list
    python task_manager.py list --all
    python task_manager.py done 1
    python task_manager.py undo 1
    python task_manager.py edit 1 "Buy oat milk"
    python task_manager.py delete 1
    python task_manager.py clear
    python task_manager.py            # interactive menu
"""

import argparse
import json
import os
from datetime import datetime

DEFAULT_FILE = os.environ.get("TASKS_FILE", "tasks.json")
PRIORITIES = ["low", "medium", "high"]


class TaskManager:
    """Stores tasks as a list of dictionaries and saves them to a JSON file."""

    def __init__(self, filename=DEFAULT_FILE):
        self.filename = filename
        self.tasks = self.load()

    # ---------- saving and loading ----------
    def load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            print(f"Warning: could not read {self.filename}, starting empty.")
            return []
        return data if isinstance(data, list) else []

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2)

    # ---------- helpers ----------
    def _next_id(self):
        return max((task["id"] for task in self.tasks), default=0) + 1

    def find(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def _require(self, task_id):
        task = self.find(task_id)
        if task is None:
            raise KeyError(f"No task with id {task_id}")
        return task

    # ---------- actions ----------
    def add(self, title, priority="medium"):
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}")
        task = {
            "id": self._next_id(),
            "title": title,
            "priority": priority,
            "done": False,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.tasks.append(task)
        self.save()
        return task

    def set_done(self, task_id, done=True):
        task = self._require(task_id)
        task["done"] = done
        self.save()
        return task

    def edit(self, task_id, title=None, priority=None):
        task = self._require(task_id)
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task["title"] = title.strip()
        if priority is not None:
            if priority not in PRIORITIES:
                raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}")
            task["priority"] = priority
        self.save()
        return task

    def delete(self, task_id):
        task = self._require(task_id)
        self.tasks.remove(task)
        self.save()
        return task

    def clear_done(self):
        before = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task["done"]]
        self.save()
        return before - len(self.tasks)

    def list(self, show_all=False):
        tasks = self.tasks if show_all else [t for t in self.tasks if not t["done"]]
        # Pending first, then highest priority first, then oldest first.
        return sorted(
            tasks,
            key=lambda t: (t["done"], -PRIORITIES.index(t["priority"]), t["id"]),
        )


def format_task(task):
    check = "x" if task["done"] else " "
    return f"[{check}] {task['id']:>3}  {task['priority']:<8}  {task['title']}"


def print_tasks(tasks):
    if not tasks:
        print("No tasks to show.")
        return
    print("     ID  PRIORITY  TITLE")
    for task in tasks:
        print(format_task(task))


# ---------- interactive menu ----------
def interactive(manager):
    menu = """
=== Task Manager ===
1. List pending tasks
2. List all tasks
3. Add task
4. Mark task done
5. Mark task not done
6. Edit task
7. Delete task
8. Clear completed tasks
0. Quit"""
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                print_tasks(manager.list())
            elif choice == "2":
                print_tasks(manager.list(show_all=True))
            elif choice == "3":
                title = input("Title: ")
                priority = input("Priority (low/medium/high) [medium]: ").strip().lower()
                task = manager.add(title, priority or "medium")
                print(f"Added task {task['id']}.")
            elif choice in ("4", "5"):
                task_id = int(input("Task id: "))
                manager.set_done(task_id, done=(choice == "4"))
                print("Updated.")
            elif choice == "6":
                task_id = int(input("Task id: "))
                title = input("New title (blank to keep): ")
                priority = input("New priority (blank to keep): ").strip().lower()
                manager.edit(task_id, title or None, priority or None)
                print("Updated.")
            elif choice == "7":
                task_id = int(input("Task id: "))
                manager.delete(task_id)
                print("Deleted.")
            elif choice == "8":
                print(f"Removed {manager.clear_done()} completed task(s).")
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again.")
        except ValueError as error:
            print(f"Error: {error}")
        except KeyError as error:
            print(f"Error: {error.args[0]}")


# ---------- command line ----------
def build_parser():
    parser = argparse.ArgumentParser(description="A simple task manager.")
    parser.add_argument("--file", default=DEFAULT_FILE, help="JSON file to store tasks in")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("add", help="add a new task")
    p.add_argument("title")
    p.add_argument("-p", "--priority", choices=PRIORITIES, default="medium")

    p = sub.add_parser("list", help="list tasks")
    p.add_argument("-a", "--all", action="store_true", help="include completed tasks")

    for name, help_text in (("done", "mark a task as done"),
                            ("undo", "mark a task as not done"),
                            ("delete", "delete a task")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("id", type=int)

    p = sub.add_parser("edit", help="change a task's title and/or priority")
    p.add_argument("id", type=int)
    p.add_argument("title", nargs="?")
    p.add_argument("-p", "--priority", choices=PRIORITIES)

    sub.add_parser("clear", help="remove all completed tasks")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    manager = TaskManager(args.file)

    if args.command is None:
        interactive(manager)
        return 0

    try:
        if args.command == "add":
            task = manager.add(args.title, args.priority)
            print(f"Added task {task['id']}: {task['title']}")
        elif args.command == "list":
            print_tasks(manager.list(show_all=args.all))
        elif args.command == "done":
            print(f"Done: {manager.set_done(args.id, True)['title']}")
        elif args.command == "undo":
            print(f"Not done: {manager.set_done(args.id, False)['title']}")
        elif args.command == "edit":
            task = manager.edit(args.id, args.title, args.priority)
            print("Updated: " + format_task(task))
        elif args.command == "delete":
            print(f"Deleted: {manager.delete(args.id)['title']}")
        elif args.command == "clear":
            print(f"Removed {manager.clear_done()} completed task(s).")
    except ValueError as error:
        print(f"Error: {error}")
        return 1
    except KeyError as error:
        print(f"Error: {error.args[0]}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
